import pyspades.contained as loaders
from pyspades.constants import *
from threading import Thread

from piqueclient.client import FeatureConnection

class Robot(FeatureConnection):
    def on_connect(self):
        print("CONNECTED: {}".format(self.peer.address))

    def on_disconnect(self):
        print("DISCONNECTED")

    def on_player_join(self, player):
        print("{} joined the game".format(player.name))

    def on_chat_message(self, player_id, chat_type, message):
        if chat_type == CHAT_ALL or chat_type == CHAT_TEAM:
            if player := self.players.get(player_id):
                print("<{}> {}".format(player.name, message))
            else:
                print(": {}".format(message))
        else:
            print(": {}".format(message))

    def send_chat(self, message):
        contained           = loaders.ChatMessage()
        contained.chat_type = CHAT_ALL
        contained.value     = message

        self.sendPacket(contained)

    def handlePacketWeaponReload(self, reader):
        contained = loaders.WeaponReload()

        if contained.player_id == self.player_id:
            print("{} / {}".format(contained.clip_ammo, contained.reserve_ammo))

robot = Robot(name = "ExampleBot")

robot.connect(b"127.0.0.1")

eventloop = Thread(target = robot.eventloop)
eventloop.start()

try:
    while True:
        robot.send_chat(input())
except KeyboardInterrupt:
    robot.disconnect()

eventloop.join()