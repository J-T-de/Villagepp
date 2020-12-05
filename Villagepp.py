from sys import exit

import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb

from PIL import ImageFont, ImageDraw, ImageTk, Image

from aiv import Aiv, AIV_SIZE, Building, BuildingId, TroopId

# TODO: settings.json
lang = "en"

# TODO: language data
lang_data = {
    "File": {
        "en": "File",
        "de": "Datei"},

    "New": {
        "en": "New",
        "de": "Neu"
    }
}


class Villagepp(tk.Tk):
    def __init__(self, master = None):
        tk.Tk.__init__(self)

        self.aiv_path = None
        self.aiv = Aiv()

        self.geometry("640x480")
        self.wm_title("Village++")
        self.iconphoto(False, tk.PhotoImage(file="res/logo.png"))

        self.frame_map       = tk.Frame(self, background = "pink")
        self.frame_navbar    = tk.Frame(self, background = "blue")
        self.frame_category  = tk.Frame(self, background = "red")
        self.frame_menu      = tk.Frame(self, background = "green")

        # populate widgets in frame
        self.map        = self.Map      (self.frame_map,     self)
        self.navbar     = self.Navbar   (self.frame_navbar,  self)
        self.category   = self.Category (self.frame_category,self)
        self.menu       = self.Menu     (self.frame_menu,    self, "Mi") 
        
        self.menubar    = self.Menubar(self)
    
        # define grid
        self.frame_map      .grid(row = 0, column = 0, sticky="nsew", rowspan = 3)
        self.frame_navbar   .grid(row = 0, column = 1, sticky="nsew")
        self.frame_category .grid(row = 1, column = 1, sticky="nsew")
        self.frame_menu     .grid(row = 2, column = 1, sticky="nsew")

        self.grid_columnconfigure(0, weight = 3)
        self.grid_columnconfigure(1, weight = 2)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 1)
        self.grid_rowconfigure(2, weight = 3)

        # all bindings
        self.bind()

    def bind(self):
        # global menubar
        self.bind_all("<Control-n>",        self.new)
        self.bind_all("<Control-o>",        self.open)
        self.bind_all("<Control-s>",        self.save)
        self.bind_all("<Control-Shift-s>",  self.save_as)
        # self.bind_all("<Control-Shift-e>",  self.export)
        self.bind_all("<Control-plus>",     self.map.zoomIn)
        self.bind_all("<Control-minus>",    self.map.zoomOut)

        # global map
        self.bind_all("<q>",            self.step_prev)
        self.bind_all("<e>",            self.step_next)
        self.bind_all("<w>",            self.map.move_north)
        self.bind_all("<a>",            self.map.move_west)
        self.bind_all("<s>",            self.map.move_south)
        self.bind_all("<d>",            self.map.move_east)
        self.bind_all("<Control-q>",    self.step_first)
        self.bind_all("<Control-e>",    self.step_last)

        # on map
        self.map.canvas.bind("<Button-1>",      self.map.clickOnMap)
        self.map.canvas.bind("<B1-Motion>",     self.map.moveMap)
        self.map.canvas.bind("<Button-3>",      self.map.unchose)
        self.map.canvas.bind("<c>",             self.map.zoomIn)
        self.map.canvas.bind("<d>",             self.map.zoomOut)
        self.map.canvas.bind("<Configure>",     self.map.resizeFrame)
        self.map.canvas.bind("<Motion>",        self.map.dragStuff)

    class Menubar(tk.Frame):
        def __init__(self, parent):
            menubar = tk.Menu(parent)
            parent.config(menu = menubar)

            # file menu
            file_menu = tk.Menu(menubar, tearoff = 0)
            menubar.add_cascade(label=lang_data["File"][lang], menu = file_menu)

            file_menu.add_command(label=lang_data["New"][lang],     command = parent.new,     accelerator = "Ctrl+N")
            file_menu.add_command(label = "Open...",                command = parent.open,    accelerator = "Ctrl+O")
            file_menu.add_command(label = "Save",                   command = parent.save,    accelerator = "Ctrl+S")
            file_menu.add_command(label = "Save as...",             command = parent.save_as, accelerator = "Ctrl+Shift+S")
            file_menu.add_separator()
            # TODO: Export Menu
            file_menu.add_command(label = "Export Preview...",      command = parent.export_preview)
            file_menu.add_command(label = "Export Full...",         command = parent.export_full)

            file_menu.add_separator()
            file_menu.add_command(label= "Exit",                    command = exit)
            
            # view menu
            view_menu = tk.Menu(menubar, tearoff = 0)
            menubar.add_cascade(label= "View", menu = view_menu)

            view_menu.add_command(label = "Zoom in",                command = parent.map.zoomIn, accelerator = "Ctrl++")
            view_menu.add_command(label = "Zoom out",               command = parent.map.zoomOut,accelerator = "Ctrl+-")

            # help menu
            help_menu = tk.Menu(menubar, tearoff = 0)   
            menubar.add_cascade(label= "Help", menu = help_menu)

            help_menu.add_command(label = "About...",               command = parent.about)

    class Map(tk.Frame):
        def __init__(self, frame_parent, parent):
            tk.Frame.__init__(self, frame_parent)

            self.canvas = tk.Canvas(frame_parent)

            self.parent = parent
            self.frame_parent = frame_parent

            self.canvas.grid(row = 0, column = 0, sticky = "nsew")
            frame_parent.columnconfigure(0, weight = 1)
            frame_parent.rowconfigure(0, weight = 1)


            self.TileSize = 32
            self.shadow = None
            #dictionaries, building/troop-id as key, corresponding tiles (of type Image) as value
            self.buildingTiles = {}
            self.troopTiles = {}
            self.loadTileset("res/tiles.bmp")

            self.mapOrigin = (0,0) #in pixel
            self.lastMousePosition = (0,0)
            self.chosenUnit = None

            self.mapSurface = Image.new("RGBA", (self.TileSize*AIV_SIZE, self.TileSize*AIV_SIZE), (0, 0, 0, 255))
            self.redrawMapSurface()

            #size of whole editor
            FrameWidth = self.canvas.winfo_width()
            FrameHeight = self.canvas.winfo_height()
            self.screenTSize = ((FrameWidth + self.TileSize - 1)//self.TileSize, (FrameHeight + self.TileSize - 1)//self.TileSize)
            self.screenSize = (FrameWidth, FrameHeight)

            blackground = Image.new("RGB", self.screenSize, (0, 0, 0))
            blackground.paste(self.mapSurface, self.mapOrigin)

            self.screen = ImageTk.PhotoImage(blackground)
            self.canvas.create_image(0, 0, image=self.screen, anchor=tk.NW)


        def zoomOut(self, event = None):
            (x0, y0) = self.mapOrigin #in units of pixel

            if(self.TileSize != 1):
                self.TileSize = self.TileSize//2
                self.resizeTileset()

                (FrameWidth, FrameHeight) = self.screenSize
                #zoomIn out to center of the screen
                self.mapOrigin = (x0//2 + FrameWidth//4, y0//2 + FrameHeight//4)

                self.screenTSize = ((FrameWidth + self.TileSize - 1)//self.TileSize, (FrameHeight + self.TileSize - 1)//self.TileSize)

                self.mapSurface = Image.new("RGBA", (self.TileSize*AIV_SIZE, self.TileSize*AIV_SIZE), (0, 0, 0, 255))
                self.redrawMapPartially((0,0), self.screenTSize)
                self.updateMapScreen()

        def zoomIn(self, event = None):
            (x0, y0) = self.mapOrigin #in units of pixel
            (FrameWidth, FrameHeight) = self.screenSize

            self.TileSize = self.TileSize*2
            self.resizeTileset()

            #zoomIn on center of the screen
            self.mapOrigin = (x0*2 - FrameWidth//2, y0*2 - FrameHeight//2)

            self.screenTSize = ((FrameWidth + self.TileSize - 1)//self.TileSize, (FrameHeight + self.TileSize - 1)//self.TileSize)


            self.mapSurface = Image.new("RGBA", (self.TileSize*AIV_SIZE, self.TileSize*AIV_SIZE), (0, 0, 0, 255))
            self.redrawMapPartially((0,0), self.screenTSize)
            self.updateMapScreen()

        def unchose(self, event):
            self.chosenUnit = None

        def mapCoords(self, position):
            (x, y) = position
            (x0, y0) = self.mapOrigin
            x = (x - x0)//self.TileSize
            y = (y - y0)//self.TileSize
            return (x, y)

        def clickOnMap(self, event):
            x = event.x
            y = event.y
            self.lastMousePosition = (x, y)
            if(self.chosenUnit != None):
                kind = self.chosenUnit[0]
                position = self.mapCoords((x, y))

                if(kind == "Building"):
                    buildingId = self.chosenUnit[1]
                    building = Building(buildingId)

                    if(self.parent.aiv.building_isplaceable(building, position)):
                        self.parent.aiv.building_place(building, position)
                        self.redrawMapPartially((x, y), building.mask_full().shape)
                elif(kind == "Unit"):
                    unitId = self.chosenUnit[1]
                    self.parent.aiv.troop_place(unitId, position)
                    self.redrawMapPartially((x, y), (1, 1))
                elif(kind == "DeleteUnit"):
                    self.parent.aiv.troop_remove(position)
                    self.redrawMapPartially((x, y), (1, 1))
                elif(kind == "DeleteBuilding"):
                    (xDelete, yDelete) = position
                    buildingId = self.parent.aiv.bmap_id[yDelete, xDelete]
                    buildingId = BuildingId(buildingId).name
                    building = Building(buildingId)
                    self.parent.aiv.building_remove(position)

                    (xSize, ySize) = building.mask_full().shape
                    #increase size that is redrawn, since the mouse could also click on the lower right of the building
                    self.redrawMapPartially((x - xSize*self.TileSize, y - ySize*self.TileSize), (2*xSize, 2*ySize))
                elif(kind == "Wall-like"):
                    #TODO: on first click: save current position
                    #      on second click: build wall/whatevs from first position to current position
                    pass

                self.updateMapScreen()

        def dragStuff(self, event):
            x = event.x
            y = event.y
            self.lastMousePosition = (x, y)
            if(self.chosenUnit != None):
                shadow = None
                (xTile, yTile) = self.mapCoords((x, y))
                kind = self.chosenUnit[0]

                if(kind == "Building"):
                    buildingId = self.chosenUnit[1]
                    building = Building(buildingId)
                    mask = building.mask_full()
                    (sizex, sizey) = mask.shape

                    tile = None
                    if(self.parent.aiv.building_isplaceable(building, (xTile, yTile))):
                        tile = Image.new("RGBA", (self.TileSize, self.TileSize), (0, 255, 0, 255))
                    else:
                        tile = Image.new("RGBA", (self.TileSize, self.TileSize), (255, 0, 0, 255))

                    shadow = Image.new("RGBA", (sizex*self.TileSize, sizey*self.TileSize), (0, 0, 0, 0))
                    for x in range(sizex):
                        for y in range(sizey):
                            shadow.paste(tile, (x*self.TileSize, y*self.TileSize))
                elif(kind == "Unit"):
                    unitId = self.chosenUnit[1]
                    shadow = Image.new("RGBA", (self.TileSize, self.TileSize), (0, 255, 0, 127))
                elif(kind == "DeleteUnit" or kind == "DeleteBuilding"):
                    shadow = Image.new("RGBA", (self.TileSize, self.TileSize), (255, 0, 0, 127))
                elif(kind == "Wall-like"):
                    pass
                    #is not yet implemented in clickOnMap
                self.shadow = shadow
                self.updateMapScreen()
            else:
                self.shadow = None
                self.updateMapScreen()

        def move_north(self, event = None):
            (x, y) = self.mapOrigin
            y += self.TileSize
            self.mapOrigin = (x, y)

            self.updateMapScreen()

        def move_south(self, event = None):
            (x, y) = self.mapOrigin
            y -= self.TileSize
            self.mapOrigin = (x, y)

            self.updateMapScreen()

        def move_east(self, event = None):
            (x, y) = self.mapOrigin
            x -= self.TileSize
            self.mapOrigin = (x, y)

            self.updateMapScreen()

        def move_west(self, event = None):
            (x, y) = self.mapOrigin
            x += self.TileSize
            self.mapOrigin = (x, y)

            self.updateMapScreen()

        def updateMapScreen(self):
            FrameWidth = self.canvas.winfo_width()
            FrameHeight = self.canvas.winfo_height()
            self.screenTSize = ((FrameWidth + self.TileSize - 1)//self.TileSize, (FrameHeight + self.TileSize - 1)//self.TileSize)
            self.screenSize = (FrameWidth, FrameHeight)

            self.screen = Image.new("RGBA", self.screenSize, (0, 0, 127, 255))
            self.screen.paste(self.mapSurface, self.mapOrigin)

            if(self.shadow != None):
                (xTile, yTile) = self.mapCoords(self.lastMousePosition)
                (x0, y0) = self.mapOrigin

                xPos = xTile*self.TileSize + x0
                yPos = yTile*self.TileSize + y0

                self.screen.paste(self.shadow, (xPos, yPos))
            self.screen = ImageTk.PhotoImage(self.screen)

            self.canvas.create_image(0, 0, image=self.screen, anchor=tk.NW)

        def moveMap(self, event):
            (x,y) = self.lastMousePosition
            moveX = event.x - x
            moveY = event.y - y

            (x, y) = self.mapOrigin
            x += moveX
            y += moveY
            self.mapOrigin = (x, y)

            (x0, y0) = self.mapOrigin #in units of pixel

            self.redrawMapPartially((0,0), self.screenTSize)

            self.updateMapScreen()

            self.lastMousePosition = (event.x, event.y)

        def resizeFrame(self, event):
            FrameWidth = self.canvas.winfo_width()
            FrameHeight = self.canvas.winfo_height()
            self.screenTSize = ((FrameWidth + self.TileSize - 1)//self.TileSize, (FrameHeight + self.TileSize - 1)//self.TileSize)
            self.screenSize = (FrameWidth, FrameHeight)

            self.redrawMapPartially(self.mapOrigin, self.screenTSize)
            self.updateMapScreen()

        def drawUnitOnMap(self, position):
            (x0, y0) = position
            (sizex, sizey) = (1,1)
            for x in range(x0, x0+sizex):
                for y in range(y0, y0+sizey):
                    troopId = self.parent.aiv.tmap[y, x]
                    if(troopId != 0):
                        troopTile = self.troopTiles[troopId]
                        background = self.mapSurface.crop((x*self.TileSize, y*self.TileSize, (x+1)*self.TileSize, (y+1)*self.TileSize))
                        newMapTile = Image.alpha_composite(background, troopTile)
                        # newMapTile.show()
                        self.mapSurface.paste(newMapTile, (x*self.TileSize, y*self.TileSize))

#        def drawBuildingOnMap(self, building, position):
#            (x0, y0) = position
#            mask = building.mask_full()
#            (sizex, sizey) = mask.shape
#
#            namePositions = []
#            for x in range(x0, x0+sizex):
#                for y in range(y0, y0+sizey):
#                    buildingId = self.parent.aiv.bmap_id[y, x]
#                    buildingSurface = None
#                    #grass
#                    if(buildingId == BuildingId.NOTHING):
#                        buildingSurface = self.buildingTiles[buildingId][self.parent.aiv.gmap[y, x]]
#                    #moat or pitch or any other tile that doesn't have an orientation - walls?
#                    elif(buildingId < 30):
#                        buildingSurface = self.buildingTiles[buildingId]
#                    else:
#                        buildingSurface = self.buildingTiles[buildingId][self.parent.aiv.bmap_tile[y, x]]
#                    if(self.parent.aiv.bmap_step[y, x] >= self.parent.aiv.step_cur):
#                        buildingSurface.putalpha(127)
#                    self.mapSurface.paste(buildingSurface, (x*self.TileSize, y*self.TileSize))
#                    if(self.parent.aiv.bmap_tile[y, x] == 1):
#                        namePositions.append((x,y))
#
#                    troopId = self.parent.aiv.tmap[y, x]
#                    if(troopId != 0):
#                        troopTile = self.troopTiles[troopId]
#
#                        background = self.mapSurface.crop((x*self.TileSize, y*self.TileSize, (x+1)*self.TileSize, (y+1)*self.TileSize))
#                        newMapTile = Image.alpha_composite(background, troopTile)
#                        self.mapSurface.paste(newMapTile, (x*self.TileSize, y*self.TileSize))


        def redrawMapPartially(self, origin, size):
            (x0, y0) = self.mapCoords(origin)
            (sizex, sizey) = size

            x0 = max(0, x0)
            y0 = max(0, y0)

            xMax = min(x0+sizex, AIV_SIZE)
            yMax = min(y0+sizey, AIV_SIZE)

            namePositions = []
            for x in range(x0, xMax):
                for y in range(y0, yMax):
                    buildingId = self.parent.aiv.bmap_id[y, x]
                    buildingSurface = None
                    #grass
                    if(buildingId == BuildingId.NOTHING):
                        buildingSurface = self.buildingTiles[buildingId][self.parent.aiv.gmap[y, x]]
                    #moat or pitch or any other tile that doesn't have an orientation - walls?
                    elif(buildingId < 30):
                        buildingSurface = self.buildingTiles[buildingId]
                    else:
                        buildingSurface = self.buildingTiles[buildingId][self.parent.aiv.bmap_tile[y, x]]
                    if(self.parent.aiv.bmap_step[y, x] >= self.parent.aiv.step_cur):
                        buildingSurface.putalpha(127)
                    self.mapSurface.paste(buildingSurface, (x*self.TileSize, y*self.TileSize))
                    if(self.parent.aiv.bmap_tile[y, x] == 1):
                        namePositions.append((x,y))

                    troopId = self.parent.aiv.tmap[y, x]
                    if(troopId != 0):
                        troopTile = self.troopTiles[troopId]

                        background = self.mapSurface.crop((x*self.TileSize, y*self.TileSize, (x+1)*self.TileSize, (y+1)*self.TileSize))
                        newMapTile = Image.alpha_composite(background, troopTile)
                        self.mapSurface.paste(newMapTile, (x*self.TileSize, y*self.TileSize))


        def redrawMapSurface(self): #redraws the map-surface, but not the screen
            self.mapSurface = Image.new("RGBA", (self.TileSize*AIV_SIZE, self.TileSize*AIV_SIZE), (0, 0, 0, 255))
            namePositions = []
            for x in range(0, AIV_SIZE): 
                for y in range(0, AIV_SIZE):
                    buildingId = self.parent.aiv.bmap_id[y, x]
                    buildingSurface = None
                    #grass
                    if(buildingId == BuildingId.NOTHING):
                        buildingSurface = self.buildingTiles[buildingId][self.parent.aiv.gmap[y, x]]
                    #moat or pitch or any other tile that doesn't have an orientation - walls?
                    elif(buildingId < 30):
                        buildingSurface = self.buildingTiles[buildingId]
                    else:
                        buildingSurface = self.buildingTiles[buildingId][self.parent.aiv.bmap_tile[y, x]]
                    if(self.parent.aiv.bmap_step[y, x] >= self.parent.aiv.step_cur):
                        buildingSurface.putalpha(127)
                    self.mapSurface.paste(buildingSurface, (x*self.TileSize, y*self.TileSize))
                    if(self.parent.aiv.bmap_tile[y, x] == 1):
                        namePositions.append((x,y))

                    #draw troops "above" buildings
                    troopId = self.parent.aiv.tmap[y, x]
                    if(troopId != 0):
                        troopTile = self.troopTiles[troopId]

                        background = self.mapSurface.crop((x*self.TileSize, y*self.TileSize, (x+1)*self.TileSize, (y+1)*self.TileSize))
                        newMapTile = Image.alpha_composite(background, troopTile)
                        self.mapSurface.paste(newMapTile, (x*self.TileSize, y*self.TileSize))
        #        for pos in namePositions:
        #            (x, y) = pos
        #            size = self.parent.aiv.bmap_size[y, x]
        #
        #            #for nice transparent text: crop underlying map, alpha_composite with text-image, then paste back to map
        #
        # #           #crop building
        # #           im = inputBMP.crop((left, upper, right, lower))
        # #           #TODO: buildings of size 2 might not get properly cropped, but atm they don't even have text since they have no tile with bmap_tile == 1
        # #           left = x - (size-1)/2
        # #           upper = y - (size-1)/2
        # #           building = self.mapSurface.crop((left, upper, right, lower))
        #
        #            #blank image for text, transparent
        #            txt = Image.new("RGBA", (self.TileSize*size, self.TileSize*size), (0, 0, 255, 0))
        #            #get a font
        #            font = ImageFont.load_default()
        #            #get a drawing context from blank image
        #            d = ImageDraw.Draw(txt)
        #            #draw text to image
        #            d.text(((self.TileSize*size)//2, (self.TileSize*size)//2), str(BuildingId(self.parent.aiv.bmap_id[y, x]).name), fill="black", anchor="mm", font=font)
        #            self.mapSurface.paste(txt, (x*self.TileSize, y*self.TileSize))

        def getInputTile(self, x, y, inputBMP):
            originOffset = 1 #first tile offset in x/y-direction
            bmpTileSize = 32 #edge length of a tile
            tileGap = 1 #space between tiles

            left = originOffset + x*(bmpTileSize + tileGap)
            upper = originOffset + y*(bmpTileSize + tileGap)
            right = left + bmpTileSize
            lower = upper + bmpTileSize

            im = inputBMP.crop((left, upper, right, lower))
            return im

        def resizeTileset(self):
            for key in self.buildingTiles:
                if(isinstance(self.buildingTiles[key], type(Image))):
                    self.buildingTiles[key] = self.buildingTiles[key].resize((self.TileSize, self.TileSize))
                elif(isinstance(self.buildingTiles[key], list)):
                    newImageList = []
                    for i in range(len(self.buildingTiles[key])):
                        newImageList.append(self.buildingTiles[key][i].resize((self.TileSize, self.TileSize)))
                    self.buildingTiles[key] = newImageList
            for key in self.troopTiles:
                self.troopTiles[key] = self.troopTiles[key].resize((self.TileSize, self.TileSize))
                        

        def loadTileset(self, path):
            rawBMP = Image.open(path)
            rawBMP.putalpha(255)
            for elem in BuildingId:
                imageList = []
                # grass
                if(elem.value == BuildingId.NOTHING):
                    for variation in range(0, 8):
                        imageList.append(self.getInputTile(8, variation, rawBMP))
                # border
                elif(elem.value == BuildingId.BORDER_TILE):
                    imageList = self.getInputTile(9, 9, rawBMP)
                # auto
                elif(elem.value == BuildingId.AUTO):
                    imageList = self.getInputTile(9, 8, rawBMP)
                # walls    
                elif(elem.value == BuildingId.HIGH_WALL):
                    imageList = self.getInputTile(0, 9, rawBMP)
                elif(elem.value == BuildingId.LOW_WALL):
                    imageList = self.getInputTile(1, 9, rawBMP)
                elif(elem.value == BuildingId.HIGH_CRENEL):
                    imageList = self.getInputTile(0, 0, rawBMP)
                elif(elem.value == BuildingId.LOW_CRENEL):
                    imageList = self.getInputTile(1, 0, rawBMP)
                #stairs
                elif(elem.value == BuildingId.STAIRS_1):
                    imageList = self.getInputTile(9, 0, rawBMP)
                elif(elem.value == BuildingId.STAIRS_2):
                    imageList = self.getInputTile(9, 1, rawBMP)
                elif(elem.value == BuildingId.STAIRS_3):
                    imageList = self.getInputTile(9, 2, rawBMP)
                elif(elem.value == BuildingId.STAIRS_4):
                    imageList = self.getInputTile(9, 3, rawBMP)
                elif(elem.value == BuildingId.STAIRS_5):
                    imageList = self.getInputTile(9, 4, rawBMP)
                elif(elem.value == BuildingId.STAIRS_6):
                    imageList = self.getInputTile(9, 5, rawBMP)
                # moat
                elif(elem.value == BuildingId.MOAT):
                    imageList = self.getInputTile(8, 8, rawBMP)
                # pitch
                elif(elem.value == BuildingId.PITCH):
                    imageList = self.getInputTile(8, 9, rawBMP)
                # else
                else:
                    for variation in range(0, 10): #10 different tile-orientations for each color
                        #imageList.append(self.getInputTile((elem.value-30)//10, variation, rawBMP))
                        imageList.append(self.getInputTile(elem.value//10 - 3, variation, rawBMP))
                self.buildingTiles.update({elem.value : imageList})
            
            for elem in TroopId:
                #blank image for text, transparent
                txt = Image.new("RGBA", (self.TileSize, self.TileSize), (255, 0, 0, 255))
                #get a font
                font = ImageFont.load_default()
                #get a drawing context from blank image
                d = ImageDraw.Draw(txt)
                #draw text to image
                d.text((self.TileSize//2, self.TileSize//2), str(elem.name), fill="black", anchor="mm", font=font)
                self.troopTiles.update({elem.value : txt})
        
        def save_image(self, path):
            self.mapSurface.save(path)

    class Navbar(tk.Frame):
        def __init__(self, frame_parent, parent):
            tk.Frame.__init__(self, frame_parent)

            self.button_firs    = tk.Button(frame_parent, text = "|<",  command = parent.step_first)
            self.button_prev    = tk.Button(frame_parent, text = "<",   command = parent.step_prev)
            self.slider_step    = tk.Scale(frame_parent, command = parent.update_slider, from_ = 1, to = parent.aiv.step_tot, orient = tk.HORIZONTAL)
            self.slider_step.set(parent.aiv.step_cur)
            self.button_next    = tk.Button(frame_parent, text = ">",   command = parent.step_next)
            self.button_last    = tk.Button(frame_parent, text = ">|",  command = parent.step_last)

            self.button_firs.grid(row = 0, column = 0, sticky="nsew")
            self.button_prev.grid(row = 0, column = 1, sticky="nsew")
            self.slider_step.grid(row = 0, column = 2, sticky="nsew")
            self.button_next.grid(row = 0, column = 3, sticky="nsew")
            self.button_last.grid(row = 0, column = 4, sticky="nsew")
            
            frame_parent.grid_columnconfigure(0, weight=1)
            frame_parent.grid_columnconfigure(1, weight=1)
            frame_parent.grid_columnconfigure(2, weight=2)
            frame_parent.grid_columnconfigure(3, weight=1)
            frame_parent.grid_columnconfigure(4, weight=1)

            frame_parent.grid_rowconfigure(0, weight=1)

    class Category(tk.Frame):
        def __init__(self, frame_parent, parent):
            tk.Frame.__init__(self, frame_parent)
            
            names = ["De", "Wa", "Ca", "Ga", "We", "In", "Mi", "Mo", "Fo", "To", "Go", "Ba"]

            for r in range(0,2):
                frame_parent.grid_rowconfigure(r, weight=1)
                for c in range (0,6):
                    frame_parent.grid_columnconfigure(c, weight=1)
                    idx = 6*r+c
                    tk.Button(frame_parent, text = names[idx], command = lambda idx=idx: self.redraw_menu(parent, names[idx])).grid(row = r, column = c, sticky="nsew")

        def redraw_menu(self, parent, category):
            parent.menu = parent.Menu(parent.frame_menu, parent, category)

    class Menu(tk.Frame):
        def __init__(self, frame_parent, parent, category = "De"):
            tk.Frame.__init__(self, frame_parent)
            self.parent = parent

            if category == "De":
                tk.Button(frame_parent, text = "POINT", command = lambda: self.set_delete_building()).grid(row = 0, column = 0, sticky="nsew", columnspan = 2)
                tk.Button(frame_parent, text = "FLOOD", command = exit).grid(row = 1, column = 0, sticky="nsew", columnspan = 2)
                for r in range(2,11):
                    tk.Button(frame_parent, text = "", command = exit).grid(row = r, column = 0, sticky="nsew", columnspan = 2)

            elif category == "Wa":
                tk.Button(frame_parent, text = "HIGH_WALL",     command = exit).grid(row = 0, column = 0, sticky="nsew", columnspan = 2)
                tk.Button(frame_parent, text = "LOW_WALL",      command = exit).grid(row = 1, column = 0, sticky="nsew", columnspan = 2)
                tk.Button(frame_parent, text = "HIGH_CRENEL",   command = exit).grid(row = 2, column = 0, sticky="nsew", columnspan = 2)
                tk.Button(frame_parent, text = "LOW_CRENEL",    command = exit).grid(row = 3, column = 0, sticky="nsew", columnspan = 2)
                tk.Button(frame_parent, text = "STAIRS",        command = exit).grid(row = 4, column = 0, sticky="nsew", columnspan = 2)
                for r in range(5,11):
                    tk.Button(frame_parent, text = "", command = exit).grid(row = r, column = 0, sticky="nsew", columnspan = 2)
            
            elif category == "Mi":
                for r in range(0,11):
                    for c in range(0,2):
                        idx = 2*r+c
                        if idx == 0:
                            tk.Button(frame_parent, text = "DELETE",    command = lambda: self.set_delete_unit()).grid(row = 0, column = 0, sticky="nsew")
                        else:
                            enum = TroopId(idx)
                            tk.Button(frame_parent, text = enum.name,   command = lambda l = enum.value: self.set_unit(l)).grid(row = r, column = c, sticky="nsew")

            elif category == "Mo":
                tk.Button(frame_parent, text = "MOAT",  command = exit).grid(row = 0, column = 0, sticky="nsew", columnspan = 2)
                tk.Button(frame_parent, text = "PITCH", command = exit).grid(row = 1, column = 0, sticky="nsew", columnspan = 2)
                for r in range(2,11):
                    tk.Button(frame_parent, text = "",  command = exit).grid(row = r, column = 0, sticky="nsew", columnspan = 2)

            else:
                base = 0
                if category == "Ca":
                    base = 30
                elif category == "Ga":
                    base = 40
                elif category == "We":
                    base = 50
                elif category == "In":
                    base = 60
                elif category == "Fo":
                    base = 70
                elif category == "To":
                    base = 80
                elif category == "Go":
                    base = 90
                elif category == "Ba":
                    base = 100
                else:
                    raise Exception("Nope")

                for r in range(0,10):
                    try:
                        enum = BuildingId(base+r)
                        tk.Button(frame_parent, text = enum.name, command = lambda l = enum.name: self.set_building(l)).grid(row = r, column = 0, sticky = "nsew", columnspan = 2)
                    except:
                        tk.Button(frame_parent, text = "", command = exit).grid(row = r, column = 0, sticky="nsew", columnspan = 2)
                tk.Button(frame_parent, text = "", command = exit).grid(row = 10, column = 0, sticky="nsew", columnspan = 2)

            for r in range(0,11):
                frame_parent.grid_rowconfigure(r, weight=1)
                for c in range(0,2):
                    frame_parent.grid_columnconfigure(c, weight=1)
        
        def set_building(self, id):
            self.parent.map.chosenUnit = ("Building", id)

        def set_unit(self, id):
            self.parent.map.chosenUnit = ("Unit", id)

        def set_delete_building(self):
            self.parent.map.chosenUnit = ("DeleteBuilding", 42)

        def set_delete_unit(self):
            self.parent.map.chosenUnit = ("DeleteUnit", 69) #nice

    def new(self, e = None):
        self.ask_save()
        self.aiv = Aiv()

        self.update_slider()

    def open(self, e = None):
        self.ask_save()
        
        aiv_path = fd.askopenfilename()

        if aiv_path == "":
            return
        else:
            self.aiv = Aiv(aiv_path)

        self.update_slider()

    def ask_save(self, e = None):
        save = mb.askyesnocancel("Village++", "Save Changes?")

        if save == True:
            self.save_as()
        elif save == False:
            return
        elif save == None:
            return

    def save(self, e = None):
        aiv_path = self.aiv_path

        if aiv_path == None:
            self.save_as()
        else:
            self.aiv.save(aiv_path)

    def save_as(self, e = None):
        aiv_path = fd.asksaveasfilename()

        if aiv_path == None:
            return
        else:
            self.aiv.save(aiv_path)

    def export_preview(self, e = None):
        save = mb.askyesno("Village++", "Do you want to export a preview?")

        if save == True:
            preview_path = fd.asksaveasfilename()
            if preview_path == None:
                return
            else:
                self.aiv.save_preview(preview_path)
        else:
            return
    
    def export_full(self, e = None):
        save = mb.askyesno("Village++", "Do you want to export an image of the full map?")

        if save == True:
            image_path = fd.asksaveasfilename()
            if image_path == None:
                return
            else:
                self.map.save_image(image_path)
        else:
            return

    def about(self, e = None):
        # TODO: implement about screen
        raise NotImplementedError

    def step_next(self, e = None):
        if (self.aiv.step_cur < self.aiv.step_tot):
            self.aiv.step_cur += 1
        self.update_slider()

    def step_prev(self, e = None):
        if (self.aiv.step_cur > 1):
            self.aiv.step_cur -= 1
        self.update_slider()

    def step_first(self, e = None):
        self.aiv.step_cur = 1
        self.update_slider()

    def step_last(self, e = None):
        self.aiv.step_cur = self.aiv.step_tot
        self.update_slider()

    def update_slider(self, e = None):
        if e != None:
            self.aiv.step_cur = int(e)
            print("step_set: ", self.aiv.step_cur, "/", self.aiv.step_tot)
            self.map.redrawMapSurface()
            self.map.updateMapScreen()
            return
        self.navbar = self.Navbar(self.frame_navbar, self)


if __name__ == "__main__":
    vpp = Villagepp()
    vpp.mainloop()