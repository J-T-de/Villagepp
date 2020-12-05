cl.exe /c crc32.c explode.c implode.c buffers.cpp
link.exe /DLL /DEF:compressionlib.def crc32.obj buffers.obj explode.obj implode.obj /OUT:compressionlib.dll