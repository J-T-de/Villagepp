from construct import Int32ul, Int32sl, Int8ul, Padding, Array, Compressed, GreedyBytes, FixedSized, Struct, this, Checksum, Pointer, Const, Bytes, Computed, Pointer, Tell
import codecs
import compression.blast_codec as blast_codec
from zlib import crc32


aiv = Struct(
    # Directory
    "dir" / Struct(
        "dir_size" / Int32ul,
        "file_size_without_directory"/ Int32ul,
        "sec_cnt" / Int32ul,
        "magic" / Const(b'\xc8\x00\x00\x00'),
        Padding(16),
        "uncompr_size" / Array(100, Int32ul),
        "compr_size" / Array(100, Int32ul),
        "id" / Array(100, Int32ul),
        "is_compr" / Array(100, Int32ul),
        "offset" / Array(100, Int32ul),
        Padding(4),
    ),

    # 2001
    "x_view" / Pointer(this.dir.dir_size + this.dir.offset[0], Int32ul),

    # 2002
    "y_view" / Pointer(this.dir.dir_size + this.dir.offset[1], Int32ul),

    # 2003
    "random_state" / Pointer(this.dir.dir_size + this.dir.offset[2], FixedSized(this.dir.uncompr_size[2], GreedyBytes)),

    # 2004
    "bmap_size" / Pointer(this.dir.dir_size + this.dir.offset[3], Struct(
        "uncompr_size" / Int32ul,
        "uncompr_size" / Computed(this._.dir.uncompr_size[3]),
        "compr_size" / Int32ul,
        "compr_size" / Computed(this._.dir.compr_size[3]-12),
        "crc32_offset" / Tell,
        "crc32" / Int32ul,
        "data" / FixedSized(this.compr_size, Compressed(Bytes(this.uncompr_size), "blast")),
        "crc32" / Pointer( this.crc32_offset, Checksum(Int32ul, lambda l: crc32(l), this.data))
    )),

    # 2005
    "bmap_tile" / Pointer(this.dir.dir_size + this.dir.offset[4], Struct(
        "uncompr_size" / Int32ul,
        "uncompr_size" / Computed(this._.dir.uncompr_size[4]),
        "compr_size" / Int32ul,
        "compr_size" / Computed(this._.dir.compr_size[4]-12),
        "crc32_offset" / Tell,
        "crc32" / Int32ul,
        "data" / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
        "crc32" / Pointer( this.crc32_offset, Checksum(Int32ul, lambda l: crc32(l), this.data))
    )),

    # 2013
    "tmap" / Pointer(this.dir.dir_size + this.dir.offset[5], Struct(
        "uncompr_size" / Int32ul,
        "uncompr_size" / Computed(this._.dir.uncompr_size[5]),
        "compr_size" / Int32ul,
        "compr_size" / Computed(this._.dir.compr_size[5]-12),
        "crc32_offset" / Tell,
        "crc32" / Int32ul,
        "data" / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
        "crc32" / Pointer( this.crc32_offset, Checksum(Int32ul, lambda l: crc32(l), this.data))
    )),

    # 2006 (keep the format close to the other map sections)
    "gmap" / Pointer(this.dir.dir_size + this.dir.offset[6], Struct(
            "data" / FixedSized(10000, GreedyBytes)
    )),

    # 2007
    "bmap_id" / Pointer(this.dir.dir_size + this.dir.offset[7], Struct(
        "uncompr_size" / Int32ul,
        "uncompr_size" / Computed(this._.dir.uncompr_size[7]),
        "compr_size" / Int32ul,
        "compr_size" / Computed(this._.dir.compr_size[7]-12),
        "crc32_offset" / Tell,
        "crc32" / Int32ul,
        "data" / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
        "crc32" / Pointer( this.crc32_offset, Checksum(Int32ul, lambda l: crc32(l), this.data))
    )),

    # 2008
    "bmap_step" / Pointer(this.dir.dir_size + this.dir.offset[8], Struct(
        "uncompr_size" / Int32ul,
        "uncompr_size" / Computed(this._.dir.uncompr_size[8]),
        "compr_size" / Int32ul,
        "compr_size" / Computed(this._.dir.compr_size[8]-12),
        "crc32_offset" / Tell,
        "crc32" / Int32ul,
        "data" / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
        "crc32" / Pointer( this.crc32_offset, Checksum(Int32ul, lambda l: crc32(l), this.data))
    )),

    # 2009
    "step_current" / Pointer(this.dir.dir_size + this.dir.offset[9], Int32ul),

    # 2010
    "step_total" / Pointer(this.dir.dir_size + this.dir.offset[10], Int32ul),
    
    # 2011
    "pause_step" / Pointer(this.dir.dir_size + this.dir.offset[11], Array(this.dir.uncompr_size[11]//4, Int32sl)),

    # 2012
    "tarr" / Pointer(this.dir.dir_size + this.dir.offset[12], Array(this.dir.uncompr_size[12]//4, Int32ul)),
    
    # 2014
    "pause" / Pointer(this.dir.dir_size + this.dir.offset[13], Int32ul)
)

codecs.register(lambda l: blast_codec.getregentry() if l=="blast" else None) 