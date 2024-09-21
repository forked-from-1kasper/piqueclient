from time import monotonic, sleep
import enet

from pyspades.constants import RIFLE_WEAPON, WEAPON_TOOL
from pyspades.bytes import ByteWriter
from pyspades.world import World

from piqueclient.packets import PacketReader, packet_attribute

class ABCConnection:
    player_id     = -1
    world_object  = None
    default_color = (0x70, 0x70, 0x70)

    def __init__(self, name = "Deuce", team = 0, weapon = RIFLE_WEAPON):
        self.name   = name
        self.team   = team
        self.weapon = weapon
        self.tool   = WEAPON_TOOL
        self.color  = self.default_color
        self.score  = 0

    def set_weapon_input(self, o):
        if wo := self.world_object:
            wo.primary_fire   = o.primary
            wo.secondary_fire = o.secondary

    def set_input_data(self, o):
        if wo := self.world_object:
            wo.set_walk(o.up, o.down, o.left, o.right)
            wo.set_animation(o.jump, o.crouch, o.sneak, o.sprint)

class BasicConnection(ABCConnection):
    physics_period = 1 / 60
    disconnected = False

    def connect(self, ip, port = 32887):
        self.time    = monotonic()
        self.players = dict()
        self.world   = World()

        self.host = enet.Host(None, 34, 1)
        self.host.compress_with_range_coder()
        self.peer = self.host.connect(enet.Address(ip, port), 1, 3)

    def disconnect(self):
        self.peer.disconnect_later()

    def sendPacket(self, contained):
        writer = ByteWriter()
        contained.write(writer)
        self.peer.send(0, enet.Packet(bytes(writer)))

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def loader_received(self, packet):
        reader = PacketReader(packet.data)
        packet_id = reader.readByte(True)

        if handler := getattr(self, packet_attribute[packet_id], None):
            handler(reader)

    def service(self):
        event = self.host.service(0)

        if event is None:
            return
        elif event.type == enet.EVENT_TYPE_CONNECT:
            self.on_connect()
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            self.peer.disconnect()

            self.disconnected = True
            self.on_disconnect()
        elif event.type == enet.EVENT_TYPE_RECEIVE:
            self.loader_received(event.packet)
        elif event.type == enet.EVENT_TYPE_NONE:
            pass

    def update(self):
        dt = monotonic() - self.time
        self.time += dt

        self.world.update(dt)
        sleep(max(0, self.physics_period - dt))

    def eventloop(self):
        while not self.disconnected:
            self.service()
            self.update()
