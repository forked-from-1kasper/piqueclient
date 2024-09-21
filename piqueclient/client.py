from itertools import product
from io import BytesIO

import zlib

from pyspades.common import Vertex3, get_color, make_color
from pyspades.world import Character, cube_line
import pyspades.contained as loaders
from pyspades.vxl import VXLData

from pyspades.constants import *

from piqueclient.network import ABCConnection, BasicConnection

def on_fall(damage):
    pass

def create_world_object(world):
    return world.create_object(Character, Vertex3(0, 0, 0), None, on_fall)

class FeatureConnection(BasicConnection):
    player_class = ABCConnection
    map_compressed_data = None

    def register_player(self, player):
        self.players[player.player_id] = player
        self.on_player_join(player)

    def get_player(self, player_id):
        if player := self.players.get(player_id):
            return player
        else:
            player = self.player_class()

            player.world_object = create_world_object(self.world)
            player.player_id    = player_id

            return player

    def get_color(self, player_id):
        if player := self.players.get(player_id):
            return player.color
        else:
            return self.default_color

    def on_chat_message(self, player_id, chat_type, message):
        pass

    def on_player_join(self, player):
        pass

    def on_player_kill(self, player, killer_id, kill_type, respawn_time):
        pass

    def on_player_leave(self, player):
        pass

    def sendSetTool(self, tool):
        contained           = loaders.SetTool()
        contained.player_id = self.player_id
        contained.value     = tool

        self.tool = tool
        self.sendPacket(contained)

    def sendSetColor(self, color):
        contained           = loaders.SetColor()
        contained.player_id = self.player_id
        contained.value     = make_color(*color)

        self.color = color
        self.sendPacket(contained)

    def sendBlockAction(self, value, x, y, z):
        contained           = loaders.BlockAction()
        contained.player_id = self.player_id
        contained.value     = value
        contained.x         = x
        contained.y         = y
        contained.z         = z

        self.sendPacket(contained)

    def sendExistingPlayer(self):
        contained           = loaders.ExistingPlayer()
        contained.player_id = self.player_id
        contained.team      = self.team
        contained.weapon    = self.weapon
        contained.tool      = self.tool
        contained.kills     = 0
        contained.color     = make_color(*self.color)
        contained.name      = self.name

        self.sendPacket(contained)

    def sendWeaponReload(self):
        contained = loaders.WeaponReload()
        self.sendPacket(contained)

    def sendWeaponInput(self, **kw):
        if wo := self.world_object:
            contained = loaders.WeaponInput()

            contained.primary   = kw.get('primary',   wo.primary_fire)
            contained.secondary = kw.get('secondary', wo.secondary_fire)

            self.set_weapon_input(contained)
            self.sendPacket(contained)

    def sendInputData(self, **kw):
        if wo := self.world_object:
            contained = loaders.InputData()

            contained.up     = kw.get('up',     wo.up)
            contained.down   = kw.get('down',   wo.down)
            contained.left   = kw.get('left',   wo.left)
            contained.right  = kw.get('right',  wo.right)
            contained.jump   = kw.get('jump',   wo.jump)
            contained.crouch = kw.get('crouch', wo.crouch)
            contained.sneak  = kw.get('sneak',  wo.sneak)
            contained.sprint = kw.get('sprint', wo.sprint)

            self.set_input_data(contained)
            self.sendPacket(contained)

    def sendOrientationData(self, ox, oy, oz):
        self.world_object.set_orientation(ox, oy, oz)

        contained = loaders.OrientationData()
        contained.x = ox
        contained.y = oy
        contained.z = oz

        self.sendPacket(contained)

    def handlePacketMapStart(self, reader):
        contained = reader.readPacket(loaders.MapStart)

        self.map_compressed_size = contained.size
        self.map_compressed_data = bytes()

    def handlePacketMapChunk(self, reader):
        contained = reader.readPacket(loaders.MapChunk)
        if self.map_compressed_data is not None:
            self.map_compressed_data += contained.data

    def handlePacketStateData(self, reader):
        contained = reader.readPacket(loaders.StateData)

        map_data = zlib.decompress(self.map_compressed_data)
        self.world.map = VXLData(BytesIO(map_data))
        self.map_compressed_data = None

        self.world_object = create_world_object(self.world)
        self.player_id    = contained.player_id

        self.world_object.dead = False

        self.sendExistingPlayer()
        self.players[self.player_id] = self

        self.on_player_join(self)

    def handlePacketExistingPlayer(self, reader):
        contained = reader.readPacket(loaders.ExistingPlayer)

        player = self.get_player(contained.player_id)

        player.team         = contained.team
        player.weapon       = contained.weapon
        player.tool         = contained.tool
        player.score        = contained.kills
        player.color        = get_color(contained.color)
        player.name         = contained.name

        player.world_object.dead = False

        if player.player_id not in self.players:
            self.register_player(player)

    def handlePacketCreatePlayer(self, reader):
        contained = reader.readPacket(loaders.CreatePlayer)

        player = self.get_player(contained.player_id)

        player.weapon = contained.weapon
        player.team   = contained.team
        player.name   = contained.name

        player.color = player.default_color

        player.world_object.set_position(contained.x, contained.y, contained.z)
        player.world_object.dead = False

        if player.player_id not in self.players:
            self.register_player(player)

    def handlePacketKillAction(self, reader):
        contained = reader.readPacket(loaders.KillAction)

        if contained.player_id != contained.killer_id:
            if killer := self.players.get(contained.killer_id):
                killer.score += 1

        if player := self.players.get(contained.player_id):
            player.world_object.dead = True
            self.on_player_kill(player, contained.killer_id, contained.kill_type, contained.respawn_time)

    def handlePacketIntelCapture(self, reader):
        contained = reader.readPacket(loaders.IntelCapture)

        if player := self.players.get(contained.player_id):
            player.score += 10

    def handlePacketPlayerLeft(self, reader):
        contained = reader.readPacket(loaders.PlayerLeft)

        if player := self.players.get(contained.player_id):
            self.world.delete_object(player.world_object)
            del self.players[contained.player_id]

            self.on_player_leave(player)

    def handlePacketWorldUpdate(self, reader):
        nitems = reader.dataLeft() // 24

        for player_id in range(nitems):
            px = reader.readFloat(False)
            py = reader.readFloat(False)
            pz = reader.readFloat(False)
            ox = reader.readFloat(False)
            oy = reader.readFloat(False)
            oz = reader.readFloat(False)

            if player := self.players.get(player_id):
                player.world_object.set_position(px, py, pz)
                player.world_object.set_orientation(ox, oy, oz)

    def handlePacketWeaponInput(self, reader):
        contained = reader.readPacket(loaders.WeaponInput)

        if player := self.players.get(contained.player_id):
            player.set_weapon_input(contained)

    def handlePacketInputData(self, reader):
        contained = reader.readPacket(loaders.InputData)

        if player := self.players.get(contained.player_id):
            player.set_input_data(contained)

    def handlePacketSetTool(self, reader):
        contained = reader.readPacket(loaders.SetTool)

        if player := self.players.get(contained.player_id):
            player.tool = contained.value

    def handlePacketSetColor(self, reader):
        contained = reader.readPacket(loaders.SetColor)

        if player := self.players.get(contained.player_id):
            player.color = get_color(contained.value)

    def handlePacketBlockAction(self, reader):
        contained = reader.readPacket(loaders.BlockAction)

        x, y, z = contained.x, contained.y, contained.z

        M = self.world.map

        if contained.value == BUILD_BLOCK:
            M.set_point(x, y, z, self.get_color(contained.player_id))

        if contained.value == DESTROY_BLOCK:
            M.destroy_point(x, y, z)

        if contained.value == SPADE_DESTROY:
            for X, Y, Z in (x, y, z - 1), (x, y, z), (x, y, z + 1):
                M.destroy_point(X, Y, Z)

        if contained.value == GRENADE_DESTROY:
            for X, Y, Z in product(range(x - 1, x + 2), range(y - 1, y + 2), range(z - 1, z + 2)):
                M.destroy_point(X, Y, Z)

    def handlePacketBlockLine(self, reader):
        contained = loaders.BlockLine()
        contained.read(reader)

        color = self.get_color(contained.player_id)

        x1, y1, z1 = contained.x1, contained.y1, contained.z1
        x2, y2, z2 = contained.x2, contained.y2, contained.z2

        for x, y, z in cube_line(x1, y1, z2, x2, y2, z2):
            self.world.map.set_point(x, y, z, color)

    def handlePacketChatMessage(self, reader):
        contained = reader.readPacket(loaders.ChatMessage)
        self.on_chat_message(contained.player_id, contained.chat_type, contained.value)
