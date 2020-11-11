#TODO:
#lvl1
#steps-karte: step-regler implementieren + entsprechende darstellung der karte
#lvl1.5
#troops - git blame julius
#build nice menus - nice text, arrangement and sorting - boxes
#lvl2
#implement 2D culling
#dateien variabel einlesen
#different resolutions
#lvl3
#make other building-buttons clickable even when a building is already chosen (check for button when action==drag_sth and then set action to choosing)

import pygame as pg
import aiv
import aiv_enums
from enum import IntEnum
import sys

debug = True
def dbgPrint(text):
    if(debug == True):
        print(text)
        
class Action(IntEnum):
    NO_ACTION = 0
    CHOOSING = 1
    DRAG_STH = 2
    DRAG_MAP = 3
    BUILD_RANGE = 4 #wall. can that be made without an extra state?
    DELETE = 5
    LOAD_FILE_DIALOGUE = 6
    SAVE_FILE_DIALOGUE = 7
    STEPS = 8

class MenuType(IntEnum):
    building = 0
    troop = 1
    menu = 2
    delete = 3
    load = 4
    save = 5
    steps = 6
    
class submenu:
    #list of buttons and type
    #geometric information is handled by the menu
    def __init__(self, buttonList, menutype, geometry, offset, btnsize, font):
        self.buttons = buttonList
        self.type = menutype #MenuType enum either building, troop or menu
        (self.width, self.height) = geometry    #geometry in amount of buttons
        self.offset = offset        #offset in pixels
        self.btnsize = btnsize
        self.font = font
        if(self.width*self.height != len(self.buttons)):
            sys.exit("Cheap variant of a compile-time error: The amount of buttons expected for the geometry is not the same as given in the buttonList")
    
    def drawSubmenu(self):
        surface = pg.Surface((self.width*self.btnsize[0], self.height*self.btnsize[1]))
        for x in range(self.width):
            for y in range(self.height):
                #textSurface, rect = self.font.render(self.buttons[x + y*self.width], (255, 255, 255))
                textSurface = self.font.render(str(self.buttons[x + y*self.width]), False, (255, 255, 255))
                surface.blit(textSurface, (x*self.btnsize[0], y*self.btnsize[1]))
        return surface

    def equalSubmenu(self, otherSubmenu):
        if(self.width != otherSubmenu.width or self.height != otherSubmenu.height):
            return False
        if(self.offset != otherSubmenu.offset):
            return False
        if(self.type != otherSubmenu.type):
            return False
        for x in range(self.width):
            for y in range(self.height):
                if(self.buttons[x + y*self.width] != otherSubmenu.buttons[x + y*self.width]):
                    return False
        return True
    
class editor:
    def __init__(self):
        #HARDCODE >>EVERYTHING<<
        self.aivLogic = aiv.Aiv()
        
        self.TILE_SIZE = 32
        self.BUTTON_SIZE = (100, 50)
        
        self.screenWidth = 800
        self.screenHeight = 600
        
        pg.init()
        #meep. freetype unter ubuntu gerade nicht verfügbar. hoffentlich funktioniert das austauschbar mit pg.font
        #self.sysfont = pg.freetype.SysFont("Shia LaBeouf.ttf", 24)
        pg.font.init()
        self.sysfont = pg.font.SysFont("Shia LaBeouf.ttf", 10)
        self.troopFont = pg.font.SysFont("Shia LaBeouf.ttf", 20)
        self.buildingNameFont = pg.font.SysFont("Shia LaBeouf.ttf", 20)
        self.submenufont = pg.font.SysFont("Shia LaBeouf.ttf", 20)
        self.gameDisplay = pg.display
        #self.gameDisplay = pg.display.set_mode((self.screenWidth, self.screenHeight))
        self.gameDisplay.set_mode((self.screenWidth, self.screenHeight))
        self.gameDisplay.set_caption('Village++')
        logo = pg.image.load("res/logo_supreme.bmp")
        self.gameDisplay.set_icon(logo)
        self.screen = self.gameDisplay.get_surface()
        
        #display stuff
        #assuming screenWidth > screenHeight. otherwise... well. TODO - schwarze streifen am rand. das ist ne gute idee
        self.mapScreen = pg.Surface((self.screenHeight, self.screenHeight))
        self.menuSize = (self.screenWidth - self.screenHeight, self.screenHeight)
        self.menuOffset = (self.screenWidth - self.menuSize[0], 0)
        self.menuScreen = pg.Surface(self.menuSize)
        
        #map internal stuff
        self.zoomLevel = 1 #err... well... was für zoom-level gibt es? TODO
        self.mapSurface = pg.Surface((self.TILE_SIZE*aiv.AIV_SIZE*self.zoomLevel, self.TILE_SIZE*aiv.AIV_SIZE*self.zoomLevel))
        self.mapXOffset = 0
        self.mapYOffset = 0
        #self.buildingSurfaces = self.loadSurfaces("")#surfaces/tiles ordered by id

        #load surfaces from single file or several files?
        self.buildingSurfaces = {} #dictionary, building/troop-id as key, corresponding building-surface as value
        self.troopSurfaces = {}
        self.loadSurfaces("res/tiles.bmp")
        
        #mix of map and action-stuff
        self.dragSurface = None
        self.chosenBuilding = None
        self.mousePosition = None
        
        #menu internal stuff
        self.chosenButton = None
        
        #menu-initializer:
        #yo, draw me some of that good stuff

        fixedBuildMenuOffset = (0,0) #aligned to upper left
        fixedBuildMenuTiles = (4,3)
        fixedBuildMenuTileSizes = (self.menuSize[0]//fixedBuildMenuTiles[0], 40) #squeezed in x-direction s.t. all buttons fit in fixedMenuBuildTiles[1] rows, 40 pixels height

        varMenuOffset = (0, fixedBuildMenuTiles[1]*fixedBuildMenuTileSizes[1] + 40)

        buildMenuBtns = ["Walls","MoatsNPitch","Castles","Gatehouse","WeaponsNTroops","Industry","Food","Town","GoodStuff","BadStuff"]
        
        WallBtns = ["HIGH_WALL", "LOW_WALL", "LOW_CRENEL", "HIGH_CRENEL", "STAIRS_1", "STAIRS_2", "STAIRS_3", "STAIRS_4", "STAIRS_5", "STAIRS_6"]
        MoatsNPitchBtns = ["MOAT", "PITCH"]
        CastlesBtns = ["TOWER_1", "TOWER_2", "TOWER_3", "TOWER_4", "TOWER_5", "OIL_SMELTER", "DOG_CAGE", "KILLING_PIT", "KEEP", "MERCENARY_POST"]
        GatehouseBtns = ["SMALL_GATEHOUSE_EW", "SMALL_GATEHOUSE_NS", "LARGE_GATEHOUSE_EW", "LARGE_GATEHOUSE_NS", "DRAWBRIDGE"]
        WeaponsNTroopsBtns = ["POLETURNER", "FLETCHER", "BLACKSMITH", "TANNER", "ARMOURER", "BARRACKS", "ARMOURY", "ENGINEERS_GUILD", "TUNNELORS_GUILD", "STABLES"]
        IndustryBtns = ["STOCKPILE", "WOODCUTTER", "QUARRY", "OX_TETHER", "IRON_MINE", "PITCH_RIG", "TRADING_POST"]
        FoodBtns = ["GRANARY", "APPLE_FARM", "DAIRY_FARM", "WHEAT_FARM", "HUNTER", "HOPS_FARM", "WIND_MILL", "BAKERY", "BREWERY", "INN"]
        TownBtns = ["HOUSE", "CHAPEL", "CHURCH", "CATHEDRAL", "HEALERS", "WELL", "WATER_POT"]
        GoodStuffBtns = ["MAYPOLE", "DANCING_BEAR", "STATUE", "SHRINE", "TOWN_GARDEN", "COMMUNAL_GARDEN", "SMALL_POND", "LARGE_POND"]
        BadStuffBtns = ["GALLOWS", "CESS_PIT", "STOCKS", "BURNING_STAKE", "DUNGEON", "RACK", "GIBBET", "CHOPPING_BLOCK", "DUNKING_STOOL"]

        buildMenus =    [submenu(WallBtns, MenuType.building, (2,5), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(MoatsNPitchBtns, MenuType.building, (1, 2), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(CastlesBtns, MenuType.building, (2, 5), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(GatehouseBtns, MenuType.building, (1, 5), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(WeaponsNTroopsBtns, MenuType.building, (2, 5), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(IndustryBtns, MenuType.building, (1, 7), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(FoodBtns, MenuType.building, (2, 5), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(TownBtns, MenuType.building, (1, 7), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(GoodStuffBtns, MenuType.building, (2, 4), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(BadStuffBtns, MenuType.building, (1, 9), varMenuOffset, self.BUTTON_SIZE, self.submenufont)]


        troopMenuBtns = ["TROOPS"]

        TroopBtns = ["OIL", "MANGONEL", "BALISTA", "TREBUCHET", "F_BALLISTA", "ARCHER", "XBOW", "SPR", "PIK", "MAC", "SWD", "KGT", "SLV", "SLR", "ASS", "SBW", "HBW", "SCM", "GRE", "BRZ", "FLG"]

        troopMenus =    [submenu(TroopBtns, MenuType.troop, (3, 7), varMenuOffset, self.BUTTON_SIZE, self.submenufont)]


        deleteMenuBtns = ["REMOVE"]

        deleteBtns = ["REMOVE_BUILDING", "REMOVE_TROOP"]

        deleteMenu =    [submenu(deleteBtns, MenuType.delete, (2,1), varMenuOffset, self.BUTTON_SIZE, self.submenufont)]
                        

        fixedBuildMenuKeys = buildMenuBtns + troopMenuBtns + deleteMenuBtns
        fixedBuildMenuValues = buildMenus + troopMenus + deleteMenu


        fixedBuildMenu = submenu(fixedBuildMenuKeys, MenuType.menu, fixedBuildMenuTiles, fixedBuildMenuOffset, fixedBuildMenuTileSizes, self.submenufont)

        #specialMenuBtns = ["LOAD", "SAVE", "REMOVE", "STEPS"]
        specialMenuBtns = ["LOAD", "SAVE", "STEPS"]

        stepBtns = ["BACKWARD", "FORWARD"]

        specialMenuTiles = (3,1)
        specialMenuTileSizes = (self.menuSize[0]//specialMenuTiles[0], 40)
        specialMenuOffset = (0, self.screenHeight - specialMenuTileSizes[1]*specialMenuTiles[1]) #aligned to lower left

        specialMenus =  [submenu(["LOAD"], MenuType.load, (1,1), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(["SAVE"], MenuType.save, (1,1), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
#                        submenu(["REMOVE"], MenuType.delete, (1,1), varMenuOffset, self.BUTTON_SIZE, self.submenufont),
                        submenu(stepBtns, MenuType.steps, (2,1), varMenuOffset, self.BUTTON_SIZE, self.submenufont)]

        specialMenu = submenu(specialMenuBtns, MenuType.menu, specialMenuTiles, specialMenuOffset, specialMenuTileSizes, self.submenufont)

        self.fixedMenus =   [fixedBuildMenu, specialMenu]


        subMenuKeys = fixedBuildMenuKeys + specialMenuBtns
        subMenuValues = fixedBuildMenuValues + specialMenus
        
        self.submenus = dict(zip(subMenuKeys, subMenuValues))
        
        #second part of menu-entry is ((width, height),(pxXOffset, pxYOffset)) - width/height in amount of buttons
        self.activeSubmenu = None

        self.action = Action.NO_ACTION
        
        #init stuff
        self.redrawMapSurface()
        self.assembleMap()
        self.drawMapOnScreen()
        self.drawMenu()
        self.drawMenuOnScreen()
        self.gameDisplay.update()
        
    def MapCoords(self, mousePosition):
        (x, y) = ((mousePosition[0] - self.mapXOffset)//self.TILE_SIZE, (mousePosition[1] - self.mapYOffset)//self.TILE_SIZE)
        if(x < 0):
            x = 0
        if(y < 0):
            y = 0
        if(x >= aiv.AIV_SIZE):
            x = aiv.AIV_SIZE - 1
        if(y >= aiv.AIV_SIZE):
            y = aiv.AIV_SIZE - 1
        return (x, y)

    def getInputTile(self, x, y, inputBMP): #starts at 0,0
        originOffset = 1    #first tile offset in x/y-direction from bmp-origin
        bmpTileSize = 32    #bmp edge length of a tile
        tileGap = 1   #horizontal distance to next column

        xTileOrigin = originOffset + x*(bmpTileSize + tileGap)
        yTileOrigin = originOffset + y*(bmpTileSize + tileGap)

        rect = pg.Rect(xTileOrigin, yTileOrigin, bmpTileSize, bmpTileSize)
        return inputBMP.subsurface(rect)
        
    def loadSurfaces(self, path):
        #self.loadDummySurfaces()
        rawBMP = pg.image.load(path)
        #get coloured surface-tiles
        for elem in aiv_enums.Building_Id:
            surfaceList = []
            if(elem == aiv_enums.Building_Id.NOTHING):#grass
                for variation in range(0, 8):
                    surfaceList.append(self.getInputTile(20, variation, rawBMP))
            elif(elem.value == aiv_enums.Building_Id.STAIRS_1):
                surfaceList.append(self.getInputTile(21, 0, rawBMP))
            elif(elem.value == aiv_enums.Building_Id.STAIRS_2):
                surfaceList.append(self.getInputTile(21, 1, rawBMP))
            elif(elem.value == aiv_enums.Building_Id.STAIRS_3):
                surfaceList.append(self.getInputTile(21, 2, rawBMP))
            elif(elem.value == aiv_enums.Building_Id.STAIRS_4):
                surfaceList.append(self.getInputTile(21, 3, rawBMP))
            elif(elem.value == aiv_enums.Building_Id.STAIRS_5):
                surfaceList.append(self.getInputTile(21, 4, rawBMP))
            elif(elem.value == aiv_enums.Building_Id.STAIRS_6):
                surfaceList.append(self.getInputTile(21, 5, rawBMP))
            else:
                for variation in range(0, 10): #10 different tile-variations for each color depending on edge
                    surfaceList.append(self.getInputTile(elem.value//10, variation, rawBMP))
            self.buildingSurfaces.update({elem.value : surfaceList})
        for elem in aiv_enums.Troop_Id:
            surface = self.troopFont.render(str(elem.name), False, (255, 0, 0))
            self.troopSurfaces.update({elem.value : surface})
    
    def loadDummySurfaces(self):
        #generate map of (enum, surface) where surface is just a surfaces of TILE_SIZE x TILE_SIZE with text from enum
        for elem in aiv_enums.Building_Id:
            #textSurface, rect = self.sysfont.render(str(elem.name), False, (255, 255, 255))
            textSurface = self.sysfont.render(str(elem.name), False, (255, 255, 255))
            buildingSurface = pg.Surface((self.TILE_SIZE, self.TILE_SIZE))
            buildingSurface.blit(textSurface, (0, 0))
            self.buildingSurfaces.update({elem.value : buildingSurface})
        
    def assembleMap(self):
        print("assembling map")
        self.mapScreen.fill(pg.Color(0,255,0))
        self.mapScreen.blit(self.mapSurface, (self.mapXOffset, self.mapYOffset))
        if(self.action == Action.DRAG_STH):
            print("assembling map with sth to drag")
            (mouseMapXCoord, mouseMapYCoord) = self.MapCoords(self.mousePosition)
            xSize, ySize = self.dragSurface.get_size()
            xSize = xSize/self.TILE_SIZE
            ySize = ySize/self.TILE_SIZE
            if(mouseMapXCoord + xSize > aiv.AIV_SIZE):
                mouseMapXCoord = aiv.AIV_SIZE - xSize
            if(mouseMapYCoord + ySize > aiv.AIV_SIZE):
                mouseMapYCoord = aiv.AIV_SIZE - ySize
            self.mapScreen.blit(self.dragSurface, (self.mapXOffset + mouseMapXCoord*self.TILE_SIZE, self.mapYOffset + mouseMapYCoord*self.TILE_SIZE))

        stepDisp = str(self.aivLogic.step_cur) + "/" + str(self.aivLogic.step_tot)
        font = pg.font.SysFont("Shia LaBeouf.ttf", 30)
        stepSurface = font.render(stepDisp, False, (255, 0, 0))
        self.mapScreen.blit(stepSurface, (0, 0))

    def updateShadow(self):
        if(self.chosenButton != None):
            if(self.chosenButton[0].type == MenuType.building):
                building = aiv.Building(self.chosenButton[1])
                ySize, xSize = building.mask_full().shape
                self.dragSurface = pg.Surface((xSize*self.TILE_SIZE, ySize*self.TILE_SIZE))
                (xPos, yPos) = self.MapCoords(self.mousePosition)
                if(xPos + xSize >= aiv.AIV_SIZE):
                    xPos = aiv.AIV_SIZE - xSize
                if(yPos + ySize >= aiv.AIV_SIZE):
                    yPos = aiv.AIV_SIZE - ySize
                if(self.aivLogic.building_isplaceable(building, (xPos, yPos))):
                    self.dragSurface.fill(pg.Color(0,255,0))
                else:
                    self.dragSurface.fill(pg.Color(255,0,0))
            if(self.chosenButton[0].type == MenuType.menu):
                pass
            if(self.chosenButton[0].type == MenuType.delete):
                self.dragSurface = pg.Surface((self.TILE_SIZE, self.TILE_SIZE))
                self.dragSurface.fill(pg.Color(255,0,0))
            #TODO
            if(self.chosenButton[0].type == MenuType.troop):
                troop = self.chosenButton[1]
                self.dragSurface = self.sysfont.render(troop, False, (255, 255, 255), (0, 0, 0))
                (xPos, yPos) = self.MapCoords(self.mousePosition)
                if(xPos >= aiv.AIV_SIZE):
                    xPos = aiv.AIV_SIZE - xSize
                if(yPos >= aiv.AIV_SIZE):
                    yPos = aiv.AIV_SIZE - ySize

#   def drawAction(self):
#       if(self.chosenButton != None):
#           building = aiv.Building(self.chosenButton[0].buttons[self.chosenButton[1] + self.chosenButton[2]*self.chosenButton[0].width])
#           pos = self.MapCoords(self.mousePosition)
#           xSize, ySize = building.mask_full().shape
#           self.dragSurface = pg.Surface(xSize*self.TILE_SIZE, ySize*self.TILE_SIZE)
#           if self.aivLogic.building_isplaceable(building, pos):
#               self.dragSurface.fill(pg.Color(0,255,0))
#           else:
#               self.dragSurface.fill(pg.Color(255,0,0))
        
    def redrawMapSurface(self): #redraws the map-surface, but not the screen
        namePositions = []
        self.mapSurface.fill(pg.Color(255,255,255))
        for x in range(0, aiv.AIV_SIZE):
            for y in range(0, aiv.AIV_SIZE):
                buildingId = self.aivLogic.bmap_id[y, x]
                #buildingStep = self.aivLogic.bmap_step[y, x]
                #if(buildingStep <= self.aivLogic.currentSte
                #gmap not implemented yet :/ git blame julius
                if(buildingId == aiv_enums.Building_Id.NOTHING):
                    self.mapSurface.blit(self.buildingSurfaces[buildingId][self.aivLogic.gmap[x,y]], (x*self.TILE_SIZE, y*self.TILE_SIZE))
                else:
                    buildingSurface = self.buildingSurfaces[buildingId][self.aivLogic.bmap_tile[y, x]].copy()
                    if(self.aivLogic.bmap_step[y, x] >= self.aivLogic.step_cur):
                        buildingSurface.set_alpha(127)
                        self.mapSurface.blit(buildingSurface, (x*self.TILE_SIZE, y*self.TILE_SIZE))
                    else:
                        #self.buildingSurfaces[buildingId][self.aivLogic.bmap_tile[y, x]], (x*self.TILE_SIZE, y*self.TILE_SIZE)
                        self.mapSurface.blit(buildingSurface, (x*self.TILE_SIZE, y*self.TILE_SIZE))
                if(self.aivLogic.bmap_tile[y, x] == 1):
                    namePositions.append((x,y))
        for pos in namePositions:
            (x, y) = pos
            size = self.aivLogic.bmap_size[y, x]
            textSurface = self.buildingNameFont.render(str(aiv_enums.Building_Id(self.aivLogic.bmap_id[y, x]).name), False, (0, 0, 0))
            (width, height) = textSurface.get_size()
            self.mapSurface.blit(textSurface, ((x + size/2 )*self.TILE_SIZE - width/2, (y + size/2)*self.TILE_SIZE - height/2))
        for x in range(0, aiv.AIV_SIZE):
            for y in range(0, aiv.AIV_SIZE):
                troopId = self.aivLogic.tmap[y, x]
                if(troopId != 0):
                    troopSurface = self.troopSurfaces[troopId]
                    tile = pg.Surface((self.TILE_SIZE, self.TILE_SIZE))
                    tile.fill(pg.Color(0, 0, 100))
                    self.mapSurface.blit(tile, (x*self.TILE_SIZE, y*self.TILE_SIZE))
                    self.mapSurface.blit(troopSurface, (x*self.TILE_SIZE + troopSurface.get_width()/2, y*self.TILE_SIZE + troopSurface.get_height()/2))

    def drawMapOnScreen(self):
        self.screen.blit(self.mapScreen, (0, 0))

    def drawMenuOnScreen(self):
        dbgPrint("Drawing menu on screen")
        self.screen.blit(self.menuScreen, self.menuOffset) #right-aligned menu
    
    def drawMenu(self):
        self.menuScreen.fill(pg.Color(0, 0, 255))
        for fmenu in self.fixedMenus:
            self.menuScreen.blit(fmenu.drawSubmenu(), fmenu.offset)
        if(self.activeSubmenu != None):
            dbgPrint("Drawing submenu to menuScreen")
            self.menuScreen.blit(self.activeSubmenu.drawSubmenu(), self.activeSubmenu.offset)
        else:
            print("No submenu to draw")
        #button über denen gehovert wird aufleuchten lassen
        #button der ausgewählt ist durchgehend aufleuchten lassen
    
    def checkButtons(self):
        MenuMousePosX = self.mousePosition[0] - self.menuOffset[0] #subtract global menu-offset
        MenuMousePosY = self.mousePosition[1] - self.menuOffset[1] #subtract global menu-offset
        #check fixed menu
        for fmenu in self.fixedMenus:
            #tmpMouseposition that is relative to fixed menu-offset
            #then the index id can be calculated by dividing by tilesize - TODO this function has to be updated for non-connected buttons
            tmpMousePosX = MenuMousePosX - fmenu.offset[0]
            tmpMousePosY = MenuMousePosY - fmenu.offset[1]
            xIndx = tmpMousePosX//fmenu.btnsize[0]
            yIndx = tmpMousePosY//fmenu.btnsize[1]
            if(xIndx >= 0 and xIndx < fmenu.width and yIndx >= 0 and yIndx < fmenu.height):
                linearIndex = xIndx + yIndx*fmenu.width
                buttonKey = fmenu.buttons[linearIndex]
                #thats a bingo
                return (fmenu, buttonKey, linearIndex)
        if(self.activeSubmenu != None):
            tmpMousePosX = MenuMousePosX - self.activeSubmenu.offset[0]
            tmpMousePosY = MenuMousePosY - self.activeSubmenu.offset[1]
            xIndx = tmpMousePosX//self.activeSubmenu.btnsize[0]
            yIndx = tmpMousePosY//self.activeSubmenu.btnsize[1]
            if(xIndx >= 0 and xIndx < self.activeSubmenu.width and yIndx >= 0 and yIndx < self.activeSubmenu.height):
                linearIndex = xIndx + yIndx*self.activeSubmenu.width
                buttonKey = self.activeSubmenu.buttons[linearIndex]
                #thats a bingo
                return (self.activeSubmenu, buttonKey, linearIndex)
        else:
            return None
            
    def equalButtons(self, otherButton): #otherButton is of same type as self.chosenButton i.e.. (subMenu, xIndx, yIndx)
        #compare if buttons contain same submenus and same index. that's the only way to identify them atm
        if(otherButton == None or self.chosenButton == None):
            return False
        if(otherButton[0].equalSubmenu(otherButton[0])):
            if(otherButton[1] == self.chosenButton[1] and otherButton[2] == self.chosenButton[2]):
                return True
        return False

    def run(self):
        clock = pg.time.Clock()
        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                else:
                    self.checkEvent(event)
                dbgPrint(event)
            #self.drawEditor()
            #pg.display.update()
            clock.tick(30) #fps
        pg.quit()


    #def loadFile(self):
    #    #textSurface, rect = self.sysfont.render("text", False, (255, 255, 255))

    #    #print sth on screen that tells you that you have to type in a file-path
    #    #TODO FIX: this is not printed unless you create an event (move mouse, ...)
    #    font = pg.font.SysFont("Shia LaBeouf.ttf", 30)
    #    loadTitle = font.render("Loading: Please enter path to aiv-file", False, (255, 255, 255), (0,0,255))

    #    titleRectCenterOnScreen = ((self.screen.get_width() - loadTitle.get_width())//2, (self.screen.get_height() - loadTitle.get_height())//2)
    #    self.screen.blit(loadTitle, titleRectCenterOnScreen)
    #    self.gameDisplay.update()

    #    #read and print input
    #    read = True
    #    load = True
    #    path = ""
    #    while read:
    #    #     pg.key.start_text_input()
    #        for event in pg.event.get():
    #            if event.type == pg.KEYDOWN and read == True: #don't handle keys send after reading has finished
    #                if event.key == pg.KEY_ESCAPE:
    #                    read = False
    #                    load = False
    #                elif event.key == pg.enter:
    #                    read = False
    #                else:
    #                    add key-string to inputstring

    #            #else:
    #                #don't do shit, only leave if enter or esc is pressed
    #            dbgPrint(event)
    #        #self.drawEditor()
    #        #pg.display.update()
    #        clock.tick(30) #fps


    #    #when enter: self.aivLogic.load(input)
    #    #self.aivLogic.load("res/pig8.aiv")


    #TODO: dokumentation - wie es sein sollte
    #was passiert wann:
    #nichts ausgewhlt:
    #                   links-klick:            
    #ausgew�hltes geb�ude:
    #                   links-klick im men�:    men� wird �berpr�ft und neues geb�ude/men� ausgew�hlt oder aktuelles geb�ude abgew�hlt
    #                   links-klick auf karte:  �berpr�fen ob platzierbar und wenn ja platzieren

    #TODO: transfer state-machine. flesh out stuff. rest should... be quite okay?

    def checkEvent(self, event):
        if(event.type == pg.MOUSEMOTION or event.type == pg.MOUSEBUTTONUP or event.type == pg.MOUSEBUTTONDOWN):
            self.mousePosition = event.pos
        #update self.mousePosition on every event!
        #events that have attribute pos:
        #MOUSEMOTION       pos, rel, buttons
        #MOUSEBUTTONUP     pos, button
        #MOUSEBUTTONDOWN   pos, button
        #change action depending on current action and event
        if(self.action == Action.NO_ACTION):
            print("no action")
            #left-click could either drags the map or chooses a button
            if(event.type == pg.MOUSEBUTTONDOWN and event.button == 1):
                #mouse on map:
                if(event.pos[0] < self.menuOffset[0] and event.pos[1] < self.screenHeight):
                    self.action = Action.DRAG_MAP
                #check if mouse is above certain button
                #chosenButton: (submenu, xIndx, yIndx)
                else:
                    self.chosenButton = self.checkButtons()
                    if self.chosenButton != None:
                        self.action = Action.CHOOSING
            else:
                #left button hasn't been clicked - nothing has been chosen
                self.chosenButton = None
        elif(self.action == Action.CHOOSING):
            print("choosing")
            if(event.type == pg.MOUSEBUTTONUP and event.button == 1):
                # - kein callback mehr: funktion fest mit submenu-type verbinden.
                # -- submenu umschalten
                # -- gebäude/truppe ausgewählt
                # -- gebäude/truppe platzieren
                # -- special function: gebäude/truppe löschen
                # -- datei laden
                # -- datei speichern
                otherButton = self.checkButtons()
                if(self.equalButtons(otherButton)):
                    print("clicked on same button")
                    print(self.chosenButton[0].type)
                    if(self.chosenButton[0].type == MenuType.building or self.chosenButton[0].type == MenuType.troop):
                        self.action = Action.DRAG_STH
                        self.updateShadow()
                        self.assembleMap()
                        self.drawMapOnScreen()
                        self.gameDisplay.update()
                    elif(self.chosenButton[0].type == MenuType.menu):
                        (submenu, buttonKey, linearIndex) = self.chosenButton
                        self.activeSubmenu = self.submenus[buttonKey]

                        self.drawMenu()
                        self.drawMenuOnScreen()
                        self.gameDisplay.update()
                        self.action = Action.NO_ACTION
                        self.chosenButton = None
                    elif(self.chosenButton[0].type == MenuType.delete):
                        self.action = Action.DRAG_STH
                        self.updateShadow()
                        self.assembleMap()
                        self.drawMapOnScreen()
                        self.gameDisplay.update()
                    elif(self.chosenButton[0].type == MenuType.load):
                        self.action = Action.LOAD_FILE_DIALOGUE
                    elif(self.chosenButton[0].type == MenuType.save):
                        self.action = Action.SAVE_FILE_DIALOGUE
                    elif(self.chosenButton[0].type == MenuType.steps):
                        self.action = Action.STEPS
                    else:
                        sys.exit(">>>>>>>>fatal error<<<<<<<<")#should be fixed. just in case.
                else:
                    self.chosenButton = None
                    self.action = Action.NO_ACTION
            else:
                #uff... really? should any other action also abort the 'choosing'-process?... yeah.
                self.chosenButton = None
                self.action = Action.NO_ACTION
        elif(self.action == Action.DRAG_STH):
            print("dragging sth")
            #check if placeable
            if(self.mousePosition[0] < self.menuOffset[0]): #stuff is only dragged when mouse is above map
                if(event.type == pg.MOUSEMOTION):
                    self.updateShadow() #if shadow moves over sth s.t. its not buildable any more it has to be updated
                    self.assembleMap()
                    self.drawMapOnScreen()
                    self.gameDisplay.update()
                if(event.type == pg.MOUSEBUTTONDOWN and event.button == 1):
                    if(self.chosenButton[0].type == MenuType.delete):
                        
                        if(self.chosenButton[1] == "REMOVE_BUILDING"):
                            dbgPrint("deleting building at {0}".format(self.mousePosition))
                            self.aivLogic.building_remove(self.MapCoords(self.mousePosition))
                        if(self.chosenButton[1] == "REMOVE_TROOP"):
                            dbgPrint("deleting troop at {0}".format(self.mousePosition))
                            self.aivLogic.troop_remove(self.MapCoords(self.mousePosition))
                    if(self.chosenButton[0].type == MenuType.building):
                        building = aiv.Building(self.chosenButton[1])
                        if(self.aivLogic.building_isplaceable(building, self.MapCoords(self.mousePosition))):
                            self.aivLogic.building_place(building, self.MapCoords(self.mousePosition))
                    if(self.chosenButton[0].type == MenuType.troop):
                        troop = aiv_enums.Troop_Id[self.chosenButton[1]]#no idea how Troop is implemented in aiv - guess its similar to Building
                        self.aivLogic.troop_place(troop, self.MapCoords(self.mousePosition))
                    self.updateShadow()
                    self.redrawMapSurface()
                    self.assembleMap()
                    self.drawMapOnScreen()
                    self.gameDisplay.update()
            if(event.type == pg.MOUSEBUTTONDOWN and event.button != 1): #any mouse button but left was clicked - cancel action
                self.chosenButton = None
                self.action = Action.NO_ACTION
                self.assembleMap()
                self.drawMapOnScreen()
                self.gameDisplay.update()
        elif(self.action == Action.DRAG_MAP):
            print("dragging map")
            if(event.type == pg.MOUSEMOTION and event.buttons == (1, 0, 0) and event.pos[0] < self.screenHeight and event.pos[1] < self.screenWidth):
                self.mapXOffset += event.rel[0]
                self.mapYOffset += event.rel[1]
                self.assembleMap()
                self.drawMapOnScreen()
                self.gameDisplay.update()
            else:
                self.action = Action.NO_ACTION
        elif(self.action == Action.LOAD_FILE_DIALOGUE):
            self.aivLogic.load("res/load.aiv")
            self.action = Action.NO_ACTION
            self.redrawMapSurface()
            self.assembleMap()
            self.drawMapOnScreen()
            self.gameDisplay.update()
        elif(self.action == Action.SAVE_FILE_DIALOGUE):
            self.aivLogic.save("out/save.aiv")
            self.action = Action.NO_ACTION
        if(self.action == Action.STEPS):
            #self.chosenButton = (fmenu, buttonKey, linearIndex)
            dbgPrint(self.chosenButton[1])
            if(self.chosenButton[1] == "BACKWARD"):
                if(self.aivLogic.step_cur > 0):
                    self.aivLogic.step_cur -= 1
                    dbgPrint("BACKWARD")
            if(self.chosenButton[1] == "FORWARD"):
                if(self.aivLogic.step_cur < self.aivLogic.step_tot):
                    self.aivLogic.step_cur += 1
                    dbgPrint("FORWARD")
            self.redrawMapSurface()
            self.assembleMap()
            self.drawMapOnScreen()
            self.gameDisplay.update()
            self.action = Action.NO_ACTION

        #    else:
        #        sys.exit("moment mal. das sollte gar nicht passieren d�rfen")


#Lauf!
editor = editor()
editor.run()
