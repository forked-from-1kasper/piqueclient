from pyspades.bytes import ByteReader

# Client <-> Server
idPacketPositionData     = 0
idPacketOrientationData  = 1
idPacketInputData        = 3
idPacketWeaponInput      = 4
idPacketGrenade          = 6
idPacketSetTool          = 7
idPacketSetColor         = 8
idPacketExistingPlayer   = 9
idPacketBlockAction      = 13
idPacketBlockLine        = 14
idPacketChatMessage      = 17
idPacketWeaponReload     = 28
idPacketChangeWeapon     = 30
idPacketExtInfo          = 60

# Client <- Server
idPacketWorldUpdate      = 2
idPacketWorldUpdate075   = idPacketWorldUpdate
idPacketWorldUpdate076   = idPacketWorldUpdate
idPacketSetHP            = 5
idPacketShortPlayerData  = 10
idPacketMoveObject       = 11
idPacketCreatePlayer     = 12
idPacketStateData        = 15
idPacketKillAction       = 16
idPacketMapStart         = 18
idPacketMapStart075      = idPacketMapStart
idPacketMapStart076      = idPacketMapStart
idPacketMapChunk         = 19
idPacketPlayerLeft       = 20
idPacketTerritoryCapture = 21
idPacketProgressBar      = 22
idPacketIntelCapture     = 23
idPacketIntelPickup      = 24
idPacketIntelDrop        = 25
idPacketRestock          = 26
idPacketFogColor         = 27
idPacketHandshakeInit    = 31
idPacketVersionGet       = 33

# Client -> Server
idPacketHit              = 5
idPacketChangeTeam       = 29
idPacketMapCached        = 31
idPacketHandshakeReturn  = 32
idPacketVersionSend      = 34

packet_attribute = {
    idPacketPositionData:      "handlePacketPositionData",
    idPacketOrientationData:   "handlePacketOrientationData",
    idPacketInputData:         "handlePacketInputData",
    idPacketWeaponInput:       "handlePacketWeaponInput",
    idPacketGrenade:           "handlePacketGrenade",
    idPacketSetTool:           "handlePacketSetTool",
    idPacketSetColor:          "handlePacketSetColor",
    idPacketExistingPlayer:    "handlePacketExistingPlayer",
    idPacketBlockAction:       "handlePacketBlockAction",
    idPacketBlockLine:         "handlePacketBlockLine",
    idPacketChatMessage:       "handlePacketChatMessage",
    idPacketExtInfo:           "handlePacketExtInfo",
    idPacketWorldUpdate:       "handlePacketWorldUpdate",
    idPacketSetHP:             "handlePacketSetHP",
    idPacketShortPlayerData:   "handlePacketShortPlayerData",
    idPacketMoveObject:        "handlePacketMoveObject",
    idPacketCreatePlayer:      "handlePacketCreatePlayer",
    idPacketStateData:         "handlePacketStateData",
    idPacketKillAction:        "handlePacketKillAction",
    idPacketMapStart:          "handlePacketMapStart",
    idPacketMapChunk:          "handlePacketMapChunk",
    idPacketPlayerLeft:        "handlePacketPlayerLeft",
    idPacketTerritoryCapture:  "handlePacketTerritoryCapture",
    idPacketProgressBar:       "handlePacketProgressBar",
    idPacketIntelCapture:      "handlePacketIntelCapture",
    idPacketIntelPickup:       "handlePacketIntelPickup",
    idPacketIntelDrop:         "handlePacketIntelDrop",
    idPacketRestock:           "handlePacketRestock",
    idPacketFogColor:          "handlePacketFogColor",
    idPacketWeaponReload:      "handlePacketWeaponReload",
    idPacketChangeWeapon:      "handlePacketChangeWeapon",
    idPacketHandshakeInit:     "handlePacketHandshakeInit",
    idPacketVersionGet:        "handlePacketVersionGet"
}

class PacketReader(ByteReader):
    def readPacket(self, klass):
        contained = klass()
        contained.read(self)

        return contained
