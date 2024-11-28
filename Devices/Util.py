import unittest


def i2bi(n, len):
    '''
    Convert integer to binary, fill zeros and reverse the order
    '''
    return bin(n)[2:].zfill(len)[::-1]



class TestDecoder(unittest.TestCase):
    def test_i2bi(self):
        print('test_i2bi')

        self.assertEqual(i2bi(0, 3), '000')
        self.assertEqual(i2bi(1, 3), '100')
        self.assertEqual(i2bi(7, 3), '111')
        self.assertEqual(i2bi(0, 4), '0000')
        self.assertEqual(i2bi(1, 4), '1000')
        self.assertEqual(i2bi(14, 4), '0111')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestDecoder('test_i2bi'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
