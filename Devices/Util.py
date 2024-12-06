import unittest


def i2b_r(num, len):
    '''
    Convert integer to binary string, fill zeros
    and reverse the order
    '''
    return bin(num)[2:].zfill(len)[::-1]

def i2b_ri(num, len):
    '''
    Convert integer to binary string, fill zeros,
    reverse the order and convert back to integer
    '''
    return list(map(int, i2b_r(num, len)))




class TestDecoder(unittest.TestCase):
    def test_i2b_r(self):
        print('test_i2b_r')

        self.assertEqual(i2b_r(0, 3), '000')
        self.assertEqual(i2b_r(1, 3), '100')
        self.assertEqual(i2b_r(7, 3), '111')
        self.assertEqual(i2b_r(0, 4), '0000')
        self.assertEqual(i2b_r(1, 4), '1000')
        self.assertEqual(i2b_r(14, 4), '0111')

    def test_i2b_ri(self):
        print('test_i2b_ri')

        self.assertEqual(i2b_ri(0, 3), [0, 0, 0])
        self.assertEqual(i2b_ri(1, 3), [1, 0, 0])
        self.assertEqual(i2b_ri(7, 3), [1, 1, 1])
        self.assertEqual(i2b_ri(0, 4), [0, 0, 0, 0])
        self.assertEqual(i2b_ri(1, 4), [1, 0, 0, 0])
        self.assertEqual(i2b_ri(14, 4), [0, 1, 1, 1])



if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestDecoder('test_i2b_r'),
        TestDecoder('test_i2b_ri'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
