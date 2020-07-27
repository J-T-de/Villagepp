import codecs
from compression import blast


### Codec APIs

def blast_encode(input, errors='strict'):
    assert errors == 'strict'
    return (blast.compress(input), len(input))

def blast_decode(input, errors='strict'):
    assert errors == 'strict'
    return (blast.decompress(input), len(input))

class Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return blast_encode(input, errors)
    def decode(self, input, errors='strict'):
        return blast_decode(input, errors)

# class IncrementalEncoder(codecs.IncrementalEncoder):
#     def encode(self, input, final=False):
#         return blast_encode(input, self.errors)[0]

# class IncrementalDecoder(codecs.IncrementalDecoder):
#     def decode(self, input, final=False):
#         return blast_decode(input, self.errors)[0]

# class StreamWriter(Codec, codecs.StreamWriter):
#     charbuffertype = bytes

# class StreamReader(Codec, codecs.StreamReader):
#     charbuffertype = bytes

### encodings module API

def getregentry():
    return codecs.CodecInfo(
        name='blast',
        encode=blast_encode,
        decode=blast_decode,
        # incrementalencoder=IncrementalEncoder,
        # incrementaldecoder=IncrementalDecoder,
        # streamreader=StreamReader,
        # streamwriter=StreamWriter,
        _is_text_encoding=False,
    )