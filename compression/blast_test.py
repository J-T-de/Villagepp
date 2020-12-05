from compression import blast
import unittest

data_compressed_4 = b'\x00\x04\x82\x24\x25\x8f\x80\x7f'
data_compressed_5 = b'\x00\x05\x82\x24\x25\x0f\x01\xff'
data_compressed_6 = b'\x00\x06\x82\x24\x25\x0f\x02\xfe\x01'

data_uncompressed = b'AIAIAIAIAIAIA'

class Testing(unittest.TestCase):
    def test_decompress(self):
        self.assertEqual(blast.decompress(data_compressed_4), data_uncompressed)
        self.assertEqual(blast.decompress(data_compressed_5), data_uncompressed)
        self.assertEqual(blast.decompress(data_compressed_6), data_uncompressed)

    def test_compress(self):
        self.assertEqual(blast.compress(data_uncompressed), data_compressed_6)

        self.assertEqual(blast.compress(data_uncompressed, level=4), data_compressed_4)
        self.assertEqual(blast.compress(data_uncompressed, level=5), data_compressed_5)
        self.assertEqual(blast.compress(data_uncompressed, level=6), data_compressed_6)

if __name__ == '__main__':
    unittest.main()