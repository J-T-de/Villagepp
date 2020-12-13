import codecs
from zlib import crc32

from construct import Struct, Int32sl, Padding, Array, Compressed, GreedyBytes, FixedSized, this, Bytes

import compression.blast_codec as blast_codec


aiv = Struct(
    # Directory
    "dir" / Struct(
        "size"      / Int32sl,  # always 2036
        "fswd"      / Int32sl,  # file size without directory
        "sec_cnt"   / Int32sl,  # always 14
        "version"   / Int32sl,  # always 200

        Padding(16),
        
        "uncompr_size"  / Array(100, Int32sl),
        "compr_size"    / Array(100, Int32sl),
        "id"            / Array(100, Int32sl),
        "is_compr"      / Array(100, Int32sl),
        "offset"        / Array(100, Int32sl),
        
        Padding(4),
    ),

    # 2001
    "x_view"    / Int32sl,

    # 2002
    "y_view"    / Int32sl,

    # 2003
    "random"    / Bytes(40016),

    # 2004
    "bmap_size" / Struct(
        "uncompr_size"  / Int32sl,
        "compr_size"    / Int32sl,
        "crc32"         / Int32sl,
        "data"          / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
    ),

    # 2005
    "bmap_tile" / Struct(
        "uncompr_size"  / Int32sl,
        "compr_size"    / Int32sl,
        "crc32"         / Int32sl,
        "data"          / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
    ),

    # 2013
    "tmap" / Struct(
        "uncompr_size"  / Int32sl,
        "compr_size"    / Int32sl,
        "crc32"         / Int32sl,
        "data"          / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
    ),

    # 2006 (keep the format close to the other map sections)
    "gmap"  / Struct(
        "data"  / FixedSized(10000, GreedyBytes)
    ),

    # 2007
    "bmap_id"   / Struct(
        "uncompr_size"  / Int32sl,
        "compr_size"    / Int32sl,
        "crc32"         / Int32sl,
        "data"          / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
    ),

    # 2008
    "bmap_step" / Struct(
        "uncompr_size"  / Int32sl,
        "compr_size"    / Int32sl,
        "crc32"         / Int32sl,
        "data"          / FixedSized(this.compr_size, Compressed(GreedyBytes, "blast")),
    ),

    # 2009
    "step_cur"  / Int32sl,

    # 2010
    "step_tot"  / Int32sl,
    
    # 2011
    "parr"      / Array(this.dir.uncompr_size[11]//4, Int32sl), # always 10 or 50 elements

    # 2012
    "tarr"      / Array(24, Array(10, Int32sl)),
    
    # 2014
    "pause"     / Int32sl
)

codecs.register(lambda l: blast_codec.getregentry() if l=="blast" else None) 