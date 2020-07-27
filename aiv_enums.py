from enum import IntEnum

class Building_Id(IntEnum):
    NOTHING     = 0
    BORDER_TILE = 1
    AUTO        = 2
    # Walls
    HIGH_WALL   = 10
    LOW_WALL    = 11
    LOW_CRENEL  = 12
    HIGH_CRENEL = 13
    STAIRS_1    = 14    # Highest
    STAIRS_2    = 15
    STAIRS_3    = 16
    STAIRS_4    = 17
    STAIRS_5    = 18    # Lowest
    STAIRS_6    = 19    # Needs to be tested
    # Moats and Pitch
    MOAT        = 20
    PITCH       = 24
    # Castles
    TOWER_1         = 30
    TOWER_2         = 31
    TOWER_3         = 32
    TOWER_4         = 33
    TOWER_5         = 34
    OIL_SMELTER     = 35
    DOG_CAGE        = 36
    KILLING_PIT     = 37
    KEEP            = 38
    MERCENARY_POST  = 39
    # Gatehouse
    SMALL_GATEHOUSE_EW  = 40
    SMALL_GATEHOUSE_NS  = 41
    LARGE_GATEHOUSE_EW  = 42
    LARGE_GATEHOUSE_NS  = 43
    DRAWBRIDGE          = 44
    # Weapons and Troops
    POLETURNER      = 50
    FLETCHER        = 51
    BLACKSMITH      = 52
    TANNER          = 53
    ARMOURER        = 54
    BARRACKS        = 55
    ARMOURY         = 56
    ENGINEERS_GUILD = 57
    TUNNELORS_GUILD = 58
    STABLES         = 59
    # Industry
    STOCKPILE       = 60
    WOODCUTTER      = 61
    QUARRY          = 62
    OX_TETHER       = 63
    IRON_MINE       = 64
    PITCH_RIG       = 65
    TRADING_POST    = 66
    # Food
    GRANARY     = 70
    APPLE_FARM  = 71
    DAIRY_FARM  = 72
    WHEAT_FARM  = 73
    HUNTER      = 74
    HOPS_FARM   = 75
    WIND_MILL   = 76
    BAKERY      = 77
    BREWERY     = 78
    INN         = 79
    # Town
    HOUSE       = 80
    CHAPEL      = 81
    CHURCH      = 82
    CATHEDRAL   = 83
    HEALERS     = 84
    WELL        = 85
    WATER_POT   = 86
    # Good Stuff
    MAYPOLE         = 90
    DANCING_BEAR    = 91
    STATUE          = 92
    SHRINE          = 93
    TOWN_GARDEN     = 94
    COMUNAL_GARDEN  = 95
    SMALL_POND      = 96
    LARGE_POND      = 97
    # Bad Stuff
    GALLOWS         = 100
    CESS_PIT        = 101
    STOCKS          = 102
    BURNING_STAKE   = 103
    DUNGEON         = 104
    RACK            = 105
    GIBBET          = 106
    CHOPPING_BLOCK  = 107
    DUNKING_STOOL   = 108


class Building_Size(IntEnum):
    NOTHING     = 1
    BORDER_TILE = 1
    AUTOMATICALLY_BUILD_THINGY = 1
    # Walls
    HIGH_WALL   = 1
    LOW_WALL    = 1
    LOW_CRENEL  = 1
    HIGH_CRENEL = 1
    STAIRS_1    = 1     # Highest
    STAIRS_2    = 1
    STAIRS_3    = 1
    STAIRS_4    = 1
    STAIRS_5    = 1     # Lowest
    STAIRS_6    = 1     # Needs to be tested
    # Moats and Pitch
    MOAT        = 1
    PITCH       = 1
    # Castles
    TOWER_1         = 3
    TOWER_2         = 4
    TOWER_3         = 5
    TOWER_4         = 6
    TOWER_5         = 6
    OIL_SMELTER     = 4
    DOG_CAGE        = 3
    KILLING_PIT     = 1
    KEEP            = 7
    MERCENARY_POST  = 5
    # Gatehouse
    SMALL_GATEHOUSE_EW  = 5
    SMALL_GATEHOUSE_NS  = 5
    LARGE_GATEHOUSE_EW  = 7
    LARGE_GATEHOUSE_NS  = 7
    DRAWBRIDGE          = 5
    # Weapons and Troops
    POLETURNER      = 4
    FLETCHER        = 4
    BLACKSMITH      = 4
    TANNER          = 4
    ARMOURER        = 4
    BARRACKS        = 4
    ARMOURY         = 4
    ENGINEERS_GUILD = 5
    TUNNELORS_GUILD = 5
    STABLES         = 6
    # Industry
    STOCKPILE       = 5
    WOODCUTTER      = 3
    QUARRY          = 7
    OX_TETHER       = 2
    IRON_MINE       = 4
    PITCH_RIG       = 4
    TRADING_POST    = 5
    # Food
    GRANARY     = 4
    APPLE_FARM  = 10    # Should be 11, relates to one of Crusader's bugs
    DAIRY_FARM  = 10
    WHEAT_FARM  = 9
    HUNTER      = 3
    HOPS_FARM   = 9
    WIND_MILL   = 3
    BAKERY      = 4
    BREWERY     = 4
    INN         = 5
    # Town
    HOUSE       = 4
    CHAPEL      = 6
    CHURCH      = 9
    CATHEDRAL   = 13
    HEALERS     = 6
    WELL        = 3
    WATER_POT   = 4
    # Good Stuff
    MAYPOLE         = 3
    DANCING_BEAR    = 5
    STATUE          = 2
    SHRINE          = 2
    TOWN_GARDEN     = 4
    COMUNAL_GARDEN  = 3
    SMALL_POND      = 5
    LARGE_POND      = 6
    # Bad Stuff
    GALLOWS         = 2
    CESS_PIT        = 5
    STOCKS          = 3
    BURNING_STAKE   = 3
    DUNGEON         = 5
    RACK            = 3
    GIBBET          = 2
    CHOPPING_BLOCK  = 3
    DUNKING_STOOL   = 5

class Troops(IntEnum):
    # Misc
    OIL     = 1
    MGL     = 2
    BAL     = 3
    TRB     = 4
    FBAL    = 5
    BOW     = 6
    XBOW    = 7
    SPR     = 8
    PIK     = 9
    MAC     = 10
    SWD     = 11
    KGT     = 12
    SLV     = 13
    SLR     = 14
    ASS     = 15
    SBW     = 16
    HBW     = 17
    SCM     = 18
    GRE     = 19
    BRZ     = 20
    FLG     = 21