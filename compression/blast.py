# This file is adapted from github.com/sourcehold/sourcehold-maps/

import struct
import ctypes
import platform
import sys

if 'windows' in platform.platform().lower():
    dll = ctypes.CDLL("compression/bin/compressionlib-nocb.dll")
elif 'linux' in platform.platform().lower():
    dll = ctypes.CDLL("compression/bin/compressionlib-nocb.so")

dll.explode_nocb.restype = ctypes.c_uint
dll.explode_nocb.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int),
                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]

dll.explode_nocb.restype = ctypes.c_void_p
dll.explode_nocb.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int),
                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]

OUTBUFFERSIZE = 1000 * 1000 * 32

def decompress(data):
    pbInBuff = ctypes.cast(data, ctypes.POINTER(ctypes.c_ubyte))
    pbInBuffEnd = len(data)

    outdata = b'\x00' * OUTBUFFERSIZE
    outdatalen = len(outdata)

    pbOutBuff = ctypes.cast(outdata, ctypes.POINTER(ctypes.c_ubyte))
    pbOutBuffEnd = ctypes.c_int(outdatalen)

    result = dll.explode_nocb(pbOutBuff, ctypes.byref(pbOutBuffEnd), pbInBuff, pbInBuffEnd)
    size = pbOutBuffEnd.value

    r = outdata[0:size]
    return b''.join(struct.pack("B", v) for v in r)


def compress(data, level=6):
    pbInBuff = ctypes.cast(data, ctypes.POINTER(ctypes.c_ubyte))
    pbInBuffEnd = len(data)

    outdata = b'\x00' * OUTBUFFERSIZE
    outdatalen = len(outdata)

    pbOutBuff = ctypes.cast(outdata, ctypes.POINTER(ctypes.c_ubyte))
    pbOutBuffEnd = ctypes.c_int(outdatalen)

    level = ctypes.c_uint(level - 3)
    type = ctypes.c_uint(0)

    result = dll.implode_nocb(pbOutBuff, ctypes.byref(pbOutBuffEnd), pbInBuff, pbInBuffEnd, type, level)

    size = pbOutBuffEnd.value

    r = outdata[0:size]

    return b''.join(struct.pack("B", v) for v in r)