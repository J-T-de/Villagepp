from enum import IntEnum
from zlib import crc32
from PIL import Image
import numpy as np

from compression import blast

AIV_DEFAULT_SIZE = 100

class Aiv(object):
    def __init__(self, path = None, aiv_size = 100):
        if (path==None):
            self.create_empty(aiv_size)
        else:
            self.load(path)

    def create_empty(self, aiv_size):
        self.aiv_size       = aiv_size

        self.dir_size       = 2036
        self.dir_fswd       = -1
        self.dir_sec_cnt    = 14
        self.dir_version    = 200

        self.dir_uncompr_size = np.array([
            4, 4, 40016, aiv_size**2, aiv_size**2, aiv_size**2, aiv_size**2, 2*aiv_size**2, 4*aiv_size**2, 4, 4, 200, 960, 4
        ], dtype=np.int32)

        self.dir_compr_size = np.array([
            4, 4, 40016, -1, -1, -1, aiv_size**2, -1, -1, 4, 4, 200, 960, 4
        ], dtype=np.int32)

        self.dir_id = np.array([
            2001, 2002, 2003, 2004, 2013, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2014
        ], dtype=np.int32)

        self.dir_is_compr = np.array([
            0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0
        ], dtype=np.int32)

        self.dir_offset = np.array([
            -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
        ], dtype=np.int32)

        self.x_view     = 0
        self.y_view     = 0
        self.random     = 40016*b'\x00'
        self.bmap_size  = np.zeros((aiv_size,aiv_size), np.int8)
        self.bmap_tile  = np.zeros((aiv_size,aiv_size), np.int8)
        self.tmap       = np.zeros((aiv_size,aiv_size), np.int8)
        self.gmap       = np.random.randint(0, 8, size=(aiv_size,aiv_size), dtype=np.int8)
        self.bmap_id    = np.zeros((aiv_size,aiv_size), np.int16)
        self.bmap_step  = np.zeros((aiv_size,aiv_size), np.int32)
        self.step_cur   = 0
        self.step_tot   = 0
        self.parr       = -1 * np.ones(50, np.int32)
        self.parr[0]    = 0
        self.tarr       = np.zeros((24,10), np.int32)
        self.pause      = 50

        # # set keep to center (can be deleted)
        # self.building_place(Building("KEEP"), ((aiv_size//2)-7,(aiv_size//2)-7))
        
        # # set border tiles into step 1
        # for i in range(0, aiv_size):
        #     self.bmap_id[0,0+i]                 = BuildingId["BORDER_TILE"]
        #     self.bmap_id[self.aiv_size-1,0+i]   = BuildingId["BORDER_TILE"]
        #     self.bmap_id[0+i,0]                 = BuildingId["BORDER_TILE"]
        #     self.bmap_id[0+i,self.aiv_size-1]   = BuildingId["BORDER_TILE"]

        #     self.bmap_step[0,0+i]               = 1
        #     self.bmap_step[self.aiv_size-1,0+i] = 1
        #     self.bmap_step[0+i,0]               = 1
        #     self.bmap_step[0+i,self.aiv_size-1] = 1

    def load(self, path):
        aiv_file = open(path, 'rb')
        aiv_data = aiv_file.read()
        aiv_file.close()

        offset  = 0     # pointer to current position in file stream
        size    = 0     # size of next block
        
        # directory size
        size = 4
        self.dir_size = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]
        offset += size

        # file size without directory
        size = 4
        self.dir_fswd = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]
        offset += size

        # sections count (always 14)
        size = 4
        self.dir_sec_cnt = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]
        offset += size

        # version (always 200)
        size = 4
        self.dir_version = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]
        offset += size

        offset += 16

        # uncompressed sizes of sections
        size = self.dir_sec_cnt * 4
        self.dir_uncompr_size   = np.frombuffer(aiv_data[offset:offset+size], np.int32).copy()
        offset += 400

        # set size
        self.aiv_size = int(self.dir_uncompr_size[3]**0.5)

        # compressed sizes of sections
        size = self.dir_sec_cnt * 4
        self.dir_compr_size     = np.frombuffer(aiv_data[offset:offset+size], np.int32).copy()
        offset += 400

        # identifier (2001-2014) of sections
        size = self.dir_sec_cnt * 4
        self.dir_id             = np.frombuffer(aiv_data[offset:offset+size], np.int32).copy()
        offset += 400

        # is section compressed?
        size = self.dir_sec_cnt * 4
        self.dir_is_compr       = np.frombuffer(aiv_data[offset:offset+size], np.int32).copy()
        offset += 400

        # section offset
        size = self.dir_sec_cnt * 4
        self.dir_offset         = np.frombuffer(aiv_data[offset:offset+size], np.int32).copy()
        offset += 400

        offset += 4

        # x view
        i = 0
        size = self.dir_compr_size[i]
        self.x_view = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]
        offset += size

        # y view
        i = 1
        size = self.dir_compr_size[i]
        self.y_view = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]
        offset += size

        # random state
        i = 2
        size = self.dir_compr_size[i]
        self.random = aiv_data[offset:offset+size]
        offset += size

        # bmap_size
        size = 12
        self.u_2004, self.c_2004, self.h_2004 = np.frombuffer(aiv_data[offset:offset+size], np.int32)
        offset += size

        size = self.c_2004
        self.bmap_size = np.frombuffer(blast.decompress(aiv_data[offset:offset+size]), np.int8).copy().reshape((self.aiv_size,self.aiv_size))
        offset += size

        # bmap_tile
        size = 12
        self.u_2005, self.c_2005, self.h_2005 = np.frombuffer(aiv_data[offset:offset+size], np.int32)
        offset += size

        size = self.c_2005
        self.bmap_tile = np.frombuffer(blast.decompress(aiv_data[offset:offset+size]), np.int8).copy().reshape((self.aiv_size,self.aiv_size))
        offset += size

        # tmap
        size = 12
        self.u_2013, self.c_2013, self.h_2015 = np.frombuffer(aiv_data[offset:offset+size], np.int32)
        offset += size

        size = self.c_2013
        self.tmap = np.frombuffer(blast.decompress(aiv_data[offset:offset+size]), np.int8).copy().reshape((self.aiv_size,self.aiv_size))
        offset += size

        # gmap
        i = 6
        size = self.dir_compr_size[i]
        self.gmap = np.frombuffer(aiv_data[offset:offset+size], np.int8).copy().reshape((self.aiv_size,self.aiv_size))
        offset += size

        # bmap_id
        size = 12
        self.u_2007, self.c_2007, self.h_2007 = np.frombuffer(aiv_data[offset:offset+size], np.int32)
        offset += size

        size = self.c_2007
        self.bmap_id = np.frombuffer(blast.decompress(aiv_data[offset:offset+size]), np.int16).copy().reshape((self.aiv_size,self.aiv_size))
        offset += size

        # bmap_step
        size = 12
        self.u_2008, self.c_2008, self.h_2008 = np.frombuffer(aiv_data[offset:offset+size], np.int32)
        offset += size

        size = self.c_2008
        self.bmap_step = np.frombuffer(blast.decompress(aiv_data[offset:offset+size]), np.int32).copy().reshape((self.aiv_size,self.aiv_size))
        offset += size

        # current step
        i = 9
        size = self.dir_compr_size[i]
        self.step_cur = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]
        offset += size

        # total steps
        i = 10
        size = self.dir_compr_size[i]
        self.step_tot = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]
        offset += size

        # steps, in which a pause occurs
        i = 11
        size = self.dir_compr_size[i]
        self.parr = np.frombuffer(aiv_data[offset:offset+size], np.int32).copy()
        offset += size

        # tarr
        i = 12
        size = self.dir_compr_size[i]
        self.tarr = np.frombuffer(aiv_data[offset:offset+size], np.int32).copy().reshape((24,10))
        offset += size

        # pause
        i = 13
        size = self.dir_compr_size[i]
        self.pause = np.frombuffer(aiv_data[offset:offset+size], np.int32)[0]

    def save(self, path):

        aiv_file = open(path, 'wb')

        aiv_data = b''

        i = 0
        size = 0
        offset = 0

        # x view
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset
        
        aiv_data += np.recarray.tobytes(np.array(self.x_view, dtype=np.int32))
        
        offset += size
        i += 1

        # y view
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset

        aiv_data += np.recarray.tobytes(np.array(self.y_view, dtype=np.int32))

        offset += size
        i += 1

        # random, TODO: watermark
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset

        aiv_data += self.random

        offset += size
        i += 1

        # bmap_size
        u = self.dir_uncompr_size[i]
        buf = np.recarray.tobytes(self.bmap_size)
        h = crc32(buf)
        buf_compr = blast.compress(buf)
        size = c = len(buf_compr)

        self.dir_compr_size[i] = size + 12
        self.dir_offset[i] = offset

        aiv_data += np.recarray.tobytes(np.array([u,c,h], dtype=np.uint32))
        aiv_data += buf_compr

        offset += size + 12
        i += 1

        # bmap_tile
        u = self.dir_uncompr_size[i]
        buf = np.recarray.tobytes(self.bmap_tile)
        h = crc32(buf)
        buf_compr = blast.compress(buf)
        size = c = len(buf_compr)

        self.dir_compr_size[i] = size + 12
        self.dir_offset[i] = offset

        aiv_data += np.recarray.tobytes(np.array([u,c,h], dtype=np.uint32))
        aiv_data += buf_compr

        offset += size + 12
        i += 1

        # tmap
        u = self.dir_uncompr_size[i]
        buf = np.recarray.tobytes(self.tmap)
        h = crc32(buf)
        buf_compr = blast.compress(buf)
        size = c = len(buf_compr)

        self.dir_compr_size[i] = size + 12
        self.dir_offset[i] = offset

        aiv_data += np.recarray.tobytes(np.array([u,c,h], dtype=np.uint32))
        aiv_data += buf_compr

        offset += size + 12
        i += 1

        # gmap
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset

        aiv_data += np.recarray.tobytes(self.gmap)

        offset += size
        i += 1

        # bmap_id
        u = self.dir_uncompr_size[i]
        buf = np.recarray.tobytes(self.bmap_id)
        h = crc32(buf)
        buf_compr = blast.compress(buf)
        size = c = len(buf_compr)

        self.dir_compr_size[i] = size + 12
        self.dir_offset[i] = offset

        aiv_data += np.recarray.tobytes(np.array([u,c,h], dtype=np.uint32))
        aiv_data += buf_compr

        offset += size + 12
        i += 1

        # bmap_step
        u = self.dir_uncompr_size[i]
        buf = np.recarray.tobytes(self.bmap_step)
        h = crc32(buf)
        buf_compr = blast.compress(buf)
        size = c = len(buf_compr)

        self.dir_compr_size[i] = size + 12
        self.dir_offset[i] = offset

        aiv_data += np.recarray.tobytes(np.array([u,c,h], dtype=np.uint32))
        aiv_data += buf_compr

        offset += size + 12
        i += 1

        # step_cur
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset
        
        aiv_data += np.recarray.tobytes(np.array(self.step_cur, dtype=np.int32))
        
        offset += size
        i += 1

        # step_tot
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset
        
        aiv_data += np.recarray.tobytes(np.array(self.step_tot, dtype=np.int32))
        
        offset += size
        i += 1

        # parr
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset
        
        aiv_data += np.recarray.tobytes(self.parr)
        
        offset += size
        i += 1

        # tarr
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset
        
        aiv_data += np.recarray.tobytes(self.tarr)
        
        offset += size
        i += 1

        # pause
        size = self.dir_uncompr_size[i]
        self.dir_compr_size[i] = size
        self.dir_offset[i] = offset
        
        aiv_data += np.recarray.tobytes(np.array(self.pause, dtype=np.int32))
        
        offset += size

        # update fswd
        self.dir_fswd = offset

        
        # create directory
        aiv_dir = b''
        
        aiv_dir = np.recarray.tobytes(np.array([self.dir_size, self.dir_fswd, self.dir_sec_cnt, self.dir_version], dtype=np.int32))
        
        aiv_dir += 16*b'\x00'

        aiv_dir += np.recarray.tobytes(self.dir_uncompr_size)
        aiv_dir += 344*b'\x00'

        aiv_dir += np.recarray.tobytes(self.dir_compr_size)
        aiv_dir += 344*b'\x00'

        aiv_dir += np.recarray.tobytes(self.dir_id)
        aiv_dir += 344*b'\x00'

        aiv_dir += np.recarray.tobytes(self.dir_is_compr)
        aiv_dir += 344*b'\x00'

        aiv_dir += np.recarray.tobytes(self.dir_offset)
        aiv_dir += 344*b'\x00'

        aiv_dir += 4*b'\x00'

        aiv_file.write(aiv_dir + aiv_data)
        aiv_file.close()

    def save_preview(self, path):
        mapping_classic = {
            0:      (0x57, 0x6F, 0x19),
            1:      (0x84, 0xA9, 0x7D),
            2:      (0x84, 0xA9, 0x7D),

            10:     (0x40, 0x40, 0x40),
            11:     (0x80, 0x80, 0x80),
            12:     (0x40, 0x40, 0x40),
            13:     (0x80, 0x80, 0x80),
            14:     (0x80, 0x80, 0x80),
            15:     (0x80, 0x80, 0x80),
            16:     (0x80, 0x80, 0x80),
            17:     (0x80, 0x80, 0x80),
            18:     (0x80, 0x80, 0x80),
            19:     (0x80, 0x80, 0x80),

            20:     (0x00, 0x00, 0xC0),
            24:     (0x00, 0x00, 0x00),

            30:     (0x40, 0x40, 0x40),
            31:     (0x40, 0x40, 0x40),
            32:     (0x40, 0x40, 0x40),
            33:     (0x40, 0x40, 0x40),
            34:     (0x40, 0x40, 0x40),
            35:     (0x40, 0x40, 0x40),
            36:     (0x40, 0x40, 0x40),
            37:     (0x40, 0x40, 0x40),
            38:     (0x40, 0x40, 0x40),
            39:     (0x40, 0x40, 0x40),

            40:     (0x80, 0x80, 0x80), 
            41:     (0x80, 0x80, 0x80), 
            42:     (0x80, 0x80, 0x80), 
            43:     (0x80, 0x80, 0x80), 
            44:     (0x80, 0x80, 0x80), 

            50:     (0xC0, 0xC0, 0xC0),
            51:     (0xC0, 0xC0, 0xC0),
            52:     (0xC0, 0xC0, 0xC0),
            53:     (0xC0, 0xC0, 0xC0),
            54:     (0xC0, 0xC0, 0xC0),
            55:     (0xC0, 0xC0, 0xC0),
            56:     (0xC0, 0xC0, 0xC0),
            57:     (0xC0, 0xC0, 0xC0),
            58:     (0xC0, 0xC0, 0xC0),
            59:     (0xC0, 0xC0, 0xC0),

            60:     (0xF8, 0xF8, 0xF8),
            61:     (0xF8, 0xF8, 0xF8),
            62:     (0xF8, 0xF8, 0xF8),
            63:     (0xF8, 0xF8, 0xF8),
            64:     (0xF8, 0xF8, 0xF8),
            65:     (0xF8, 0xF8, 0xF8),
            66:     (0xF8, 0xF8, 0xF8),

            70:     (0xF8, 0xF8, 0xC8),
            71:     (0xF8, 0xF8, 0xC8),
            72:     (0xF8, 0xF8, 0xC8),
            73:     (0xF8, 0xF8, 0xC8),
            74:     (0xF8, 0xF8, 0xC8),
            75:     (0xF8, 0xF8, 0xC8),
            76:     (0xF8, 0xF8, 0xC8),
            77:     (0xF8, 0xF8, 0xC8),
            78:     (0xF8, 0xF8, 0xC8),
            79:     (0xF8, 0xF8, 0xC8),

            80:     (0xF8, 0xF8, 0x40),
            81:     (0xF8, 0xF8, 0x40),
            82:     (0xF8, 0xF8, 0x40),
            83:     (0xF8, 0xF8, 0x40),
            84:     (0xF8, 0xF8, 0x40),
            85:     (0xF8, 0xF8, 0x40),
            86:     (0xF8, 0xF8, 0x40),

            90:     (0xC0, 0xC0, 0xF8),
            91:     (0xC0, 0xC0, 0xF8),
            92:     (0xC0, 0xC0, 0xF8),
            93:     (0xC0, 0xC0, 0xF8),
            94:     (0xC0, 0xC0, 0xF8),
            95:     (0xC0, 0xC0, 0xF8),
            96:     (0xC0, 0xC0, 0xF8),
            97:     (0xC0, 0xC0, 0xF8),

            100:    (0xF8, 0x80, 0x80),
            101:    (0xF8, 0x80, 0x80),
            102:    (0xF8, 0x80, 0x80),
            103:    (0xF8, 0x80, 0x80),
            104:    (0xF8, 0x80, 0x80),
            105:    (0xF8, 0x80, 0x80),
            106:    (0xF8, 0x80, 0x80),
            107:    (0xF8, 0x80, 0x80),
            108:    (0xF8, 0x80, 0x80)} 

        mat = np.zeros((self.aiv_size, self.aiv_size, 3), dtype=np.uint8)

        for i in range(0, self.aiv_size):
            for j in range(0, self.aiv_size):
                mat[i,j] = mapping_classic[self.bmap_id[i,j]]

        image = Image.fromarray(mat, "RGB")

        image.save(path)

    def building_isplaceable(self, building, pos):
        """
        returns true if building is placeable at pos, else false
        """
        x_pos, y_pos = pos
        m = building.mask_full()
        y_size, x_size = m.shape

        if x_pos < 0 or x_pos + x_size > self.aiv_size or y_pos < 0 or y_pos + y_size > self.aiv_size:
            return False

        for x in range(0,x_size):
            for y in range(0,y_size):
                if m[y,x] == 1:
                    if self.bmap_id[y_pos+y, x_pos+x] != 0:
                        return False
        return True

    def building_place(self, building, pos, pause=False):
        """
        places building at pos with pause, does nothing if building is not placable
        """
        if not self.building_isplaceable(building, pos):
            return
        
        x_pos, y_pos = pos

        # Update current step and total steps
        self.step_cur += 1
        self.step_tot += 1

        # all later steps +1
        for x in range(0, self.aiv_size):
            for y in range(0, self.aiv_size):
                if (self.bmap_step[y, x] >= self.step_cur):
                    self.bmap_step[y, x] += 1

        # Update bmap_id and bmap_step 
        m_id = building.mask_id()
        m_step = building.mask_step(self.step_cur)
        y_size, x_size = m_id.shape

        for x in range(0,x_size):
            for y in range(0,y_size):
                self.bmap_id[y_pos+y, x_pos+x] += m_id[y,x]
                self.bmap_step[y_pos+y, x_pos+x] += m_step[y,x]

        # Update bmap_size and bmap_tile
        m_size = building.mask_size()
        m_tile = building.mask_tile()
        y_size, x_size = m_size.shape

        for x in range(0,x_size):
            for y in range(0,y_size):
                self.bmap_size[y_pos+y, x_pos+x] += m_size[y,x]
                self.bmap_tile[y_pos+y, x_pos+x] += m_tile[y,x]

    def building_remove(self, pos):
        """
        removes building placed at pos
        """
        x, y = pos
        step = self.bmap_step[y,x] # building-step to delete

        if step == 0:
            return

        for x in range(0, self.aiv_size):
            for y in range(0, self.aiv_size):
                tile_step = self.bmap_step[y,x] # building-step of the current tile
                if (tile_step == step):         # delete building
                    self.bmap_step[y,x]  = 0
                    self.bmap_id[y,x]    = 0
                    self.bmap_size[y,x]  = 0
                    self.bmap_tile[y,x]  = 0
                elif tile_step > step:
                    self.bmap_step[y,x]  -= 1 # all steps after the deleted step need to be decremented

        if self.step_cur == self.step_tot:
            self.step_cur -= 1
        self.step_tot -= 1

    def troop_place(self, troop, pos):
        """
        places troop at pos
        """
        x, y = pos

        # if there are less then 10 troops place, write the tile-id into  tarr
        for i in range(0, 10):
            if self.tarr[troop][i] == 0:
                tile_id = self.aiv_size * y + x
                self.tarr[troop][i] = tile_id
                break
        else:
            return  # return if there is no empty spot
        
        # also draw unit on tmap
        self.tmap[y, x] = troop

    def troop_remove(self, pos):
        """
        removes troop at pos
        """
        x, y = pos
        tile_id = self.aiv_size * y + x

        # find which troop is visible on pos
        troop = self.tmap[y,x]
        if troop == 0:
            return

        # remove troop from tarr and shift all following up
        for i in range(1, 10):
            if self.tarr[troop][i] == tile_id:
                idx = i
                break
        
        # shift all other units
        for i in range(idx,9):
            self.tarr[troop][i] = self.tarr[troop][i+1]
        self.tarr[troop][9] = 0
        
        # find new unit to render on tmap
        for t in range(0, 24):
            for i in range(0,10):
                if self.tarr[t][i] == tile_id:
                    self.tmap[y, x] = t
                    return
        else:
            self.tmap[y,x] = 0

    def pause_add(self, step):
        for i in range(1, len(self.parr)):
            el = self.parr[i]
            if (step > el):
                continue
            elif (step == el):
                return
            else:
                self.parr[i+1:] = self.parr[i:-1]
                self.parr[i] = step
                return
        for i in range(0, len(self.parr)):
            el = self.parr[i]
            if (el == -1):
                self.parr[i] = step
                return       

    def pause_remove(self, step):
        for i in range(1, len(self.parr)):
            if (self.parr[i] == step):
                for j in range(i, len(self.parr)-1):
                    self.parr[j] = self.parr[j+1]
                else:
                    self.parr[-1] = -1

    def move_pos(self, dir):
        """
        moves all buildings in the desired direction N, W, S, E by one; does nothing if not possible
        """
        raise NotImplementedError
        # if dir == 'N':
        #     if np.all(aiv[0,:] == 0):
        #         aiv[:-1,:] = aiv[1:,:]
        #         aiv[-1,:] = np.zeros((1,self.aiv_size))
        # elif dir == 'W':
        #     if np.all(aiv[:,0] == 0):
        #         aiv[:,:-1] = aiv[:,1:]
        #         aiv[:,-1] = np.zeros(self.aiv_size)
        # elif dir == 'S':
        #     if np.all(aiv[-1,:] == 0):
        #         aiv[1:,:] = aiv[:-1,:]
        #         aiv[1,:] = np.zeros((1,self.aiv_size))
        # elif dir == 'E':
        #     if np.all(aiv[:,-1] == 0):
        #         aiv[:,1:] = aiv[:,:-1]
        #         aiv[:,1] = np.zeros(self.aiv_size)
        # return

    def move_time(self, step_before, step_after):
        """
        moves building built at step_before to step_after
        """
        raise NotImplementedError

    def _bresenham(self, building, pos_start, pos_end):
        """
        implements bresenham algorithm for line drawing (from wikipedia)
        """
        x0, y0 = pos_start
        x1, y1 = pos_end

        origin = (min(x0,x1), min(y0,y1))
        mask = np.zeros((self.aiv_size, self.aiv_size))
        
        dx =  abs(x1-x0)
        if x0 < x1:
            sx = 1
        else:
            sx = -1
    
        dy = -abs(y1-y0)
        if y0 < y1:
            sy = 1
        else:
            sy = -1
        
        err = dx + dy

        building_id = building.id

        stairlike = False
        if building.name in ["STAIRS_1", "STAIRS_2", "STAIRS_3", "STAIRS_4", "STAIRS_5", "STAIRS_6"]:
            stairlike = True

        while True:
            if stairlike:
                if building_id <= Building("STAIRS_6").id:
                    mask[y0, x0] = building_id
                    building_id += 1
                else:
                    mask[y0,x0] = 0
            else:
                mask[y0, x0] = building_id
            
            if x0 == x1 and y0 == y1:
                break

            e2 = 2*err
            if (e2 >= dy):
                err += dy
                x0 += sx
            if (e2 <= dx):
                err += dx
                y0 += sy

        return (origin, mask[origin[1]:origin[1]+ abs(dy) + 1, origin[0]:origin[0] + abs(dx) + 1])        

    def wall_isplaceable(self, building, pos_start, pos_end, thickness=1):
        """
        returns true if wall is placeable, else false
        """
        if thickness != 1:
            raise NotImplementedError

        (x_pos, y_pos), m = self._bresenham(building, pos_start, pos_end)
        y_size, x_size = m.shape

        if x_pos < 0 or x_pos + x_size > self.aiv_size or y_pos < 0 or y_pos + y_size > self.aiv_size:
            return False

        for x in range(0, x_size):
            for y in range(0, y_size):
                if m[y,x] != 0:
                    if self.bmap_id[y_pos+y, x_pos+x] != 0:
                        return False
        return True

    def wall_mask(self, building, pos_start, pos_end, thickness=1):
        """
        builds a wall of type building from pos1 to pos2 with thickness
        """
        if thickness != 1:
            raise NotImplementedError

        return self._bresenham(building, pos_start, pos_end)
        
    def wall_place(self, building, pos_start, pos_end, thickness=1):
        """
        builds a wall of building from pos1 to pos2 with thickness
        """
        if thickness != 1:
            raise NotImplementedError

        if not self.wall_isplaceable(building, pos_start, pos_end, thickness=1):
            return

        # Update bmap_id and bmap_step 
        (x_pos, y_pos), m = self._bresenham(building, pos_start, pos_end)
        y_size, x_size = m.shape

        if building.name not in ["STAIRS_1", "STAIRS_2", "STAIRS_3", "STAIRS_4", "STAIRS_5", "STAIRS_6"]:

            # Update current step and total steps
            self.step_cur += 1
            self.step_tot += 1

            # all later steps +1
            for x in range(0, self.aiv_size):
                for y in range(0, self.aiv_size):
                    if (self.bmap_step[y, x] >= self.step_cur):
                        self.bmap_step[y, x] += 1
            for x in range(0,x_size):
                for y in range(0,y_size):
                    self.bmap_id[y_pos+y, x_pos+x] += m[y,x]
                    if m[y,x] > 0:
                        self.bmap_step[y_pos+y, x_pos+x]    += self.step_cur
                        self.bmap_size[y_pos+y, x_pos+x]    += 1
                        self.bmap_tile[y_pos+y, x_pos+x]    += 1
        else: # stairs
            max = int(np.max(m))
            min = int(np.min(m[np.nonzero(m)]))
            for stair in range(min, max + 1):
                for x in range(0, x_size):
                    for y in range(0, y_size):
                        if m[y,x] == stair:
                            self.building_place(Building(BuildingId(stair).name), (x_pos + x, y_pos + y))

    def moat_pitch_isplaceable(self, pos, thickness = 1):
        x_pos, y_pos = pos
        x_size, y_size = (thickness, thickness)

        if x_pos < 0 or x_pos + x_size > self.aiv_size or y_pos < 0 or y_pos + y_size > self.aiv_size:
            return False

        for x in range(0, x_size):
            for y in range(0, y_size):
                if self.bmap_id[y_pos+y, x_pos+x] == 0:
                    return True
        
        return False

    def moat_pitch_mask(self, building, mask, pos, thickness = 1):
        x_pos, y_pos = pos
        x_size, y_size = (thickness, thickness)

        for x in range(0, x_size):
            for y in range(0, y_size):
                if self.bmap_id[y_pos + y, x_pos + x] == 0:
                    mask[y_pos + y, x_pos + x] = building.id
        return mask

    def moat_pitch_place(self, building, mask):
        for x in range(0, self.aiv_size):
            for y in range(0, self.aiv_size):
                if mask[y,x] != 0 and self.bmap_id[y,x] == 0:
                    self.bmap_id[y,x] = building.id

    def merge_steps(self, steps):
        """
        merges steps into the steps with the lowest number
        """
        raise NotImplementedError

    def flood_fill(self, TODO):
        """
        fills 
        """
        raise NotImplementedError

    def flood_remove(self, TODO):
        """
        removes 
        """
        raise NotImplementedError

class Building():
    def __init__(self, name):
        self.name = name
        self.size = BuildingSize[name]
        self.id = BuildingId[name]
    
    def mask(self):
        """
        returns the mask of the building
        """
        return np.ones((self.size, self.size))

    def mask_full(self):
        """
        returns the mask of the building including the automatically built place-holders
        """
        size = self.size

        if self.name == "KEEP":
            m = np.zeros((2*size+1,size+5), dtype = np.int8)
            m[:size,:size] = np.ones((size,size))           # keep
            m[size:size+1,2:5] = np.ones((1,3))             # keepdoor
            m[size+1:2*size+1,:size] = np.ones((size,size)) # campfire
            m[2:7,size:size+5] = np.ones((5,5))             # stockpile
        elif self.name in ["OIL_SMELTER", "ENGINEERS_GUILD", "TUNNELORS_GUILD"]:
            m = np.ones((2*size, size), dtype=np.int8)
        elif self.name in ["MERCENARY_POST", "BARRACKS"]:
            m = np.ones((2*size, 2*size), dtype=np.int8)
        else:
            m = self.mask()
        return m

    def mask_id(self):
        """
        returns the mask with all building ids for bmap_id
        """
        m = 2 * self.mask_full()
        m[0:self.size, 0:self.size] = self.id * self.mask()
        return m.astype(np.int16)

    def mask_step(self, step):
        """
        returns the mask with all building steps for bmap_step
        """
        m = step * self.mask_full()
        return m.astype(np.int32)

    def mask_tile(self):
        """
        returns mask for bmap_tile
        """
        if self.size == 1:
            m = np.array([[0]])
        elif self.size ==2:
            m = np.array([[1,2],[4,3]])
        else:
            m           = 9 * np.ones((self.size, self.size))
            m[0,0]      = 1
            m[0,-1]     = 2
            m[-1,-1]    = 3
            m[-1,0]     = 4 
            m[0,1:-1]   = 5 * np.ones(self.size-2)
            m[1:-1,-1]  = 6 * np.ones(self.size-2)
            m[-1,1:-1]  = 7 * np.ones(self.size-2)
            m[1:-1,0]   = 8 * np.ones(self.size-2)
        return m.astype(np.int8)

    def mask_size(self):
        """
        returns mask for bmap_size
        """
        m = self.size * self.mask()
        return m.astype(np.int8)

class BuildingId(IntEnum):
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

class BuildingSize(IntEnum):
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
    QUARRY          = 6
    OX_TETHER       = 2
    IRON_MINE       = 4
    PITCH_RIG       = 4
    TRADING_POST    = 5
    # Food
    GRANARY     = 4
    APPLE_FARM  = 11
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

class TroopId(IntEnum):
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
