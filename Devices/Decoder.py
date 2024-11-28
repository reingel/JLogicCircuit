import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Branch import Branch
from Gate import And, AndN, OrN, Inverter

def i2bi(n, len):
    return bin(n)[2:].zfill(len)[::-1]


class Decoder(SimulatedCircuit):
    # W: 1 bit (Write)
    # A: Address
    # O: Output, one-hot
    def __init__(self, name, n):
        self.device_name = 'Decoder'
        self.name = name

        self.naddr = n
        self.nmem = 2**n

        # create elements
        self.brnd = [Branch(f'brnd{i}') for i in range(self.naddr)] # branch directly connected
        self.inv = [Inverter(f'inv{i}') for i in range(self.naddr)]
        self.brni = [Branch(f'brni{i}') for i in range(self.naddr)] # branch connected through inverter
        self.ando = [AndN(f'and{i}', 4) for i in range(self.nmem)]
        
        # connect
        for i in range(self.naddr):
            self.brnd[i] >> self.inv[i].I
            self.inv[i].O >> self.brni[i]
            for j in range(self.nmem):
                bin = i2bi(j, self.naddr)
                (self.brnd[i] if bin[i] == '1' else self.brni[i]) >> self.ando[j].I[i]

        # create access points
        self.A = self.brnd
        self.O = [self.ando[i].O for i in range(self.nmem)]

        # update sequences
        self.update_sequence = [self.brnd[i] for i in range(self.naddr)]
        self.update_sequence.extend([self.inv[i] for i in range(self.naddr)])
        self.update_sequence.extend([self.brni[i] for i in range(self.naddr)])
        self.update_sequence.extend([self.ando[j] for j in range(self.nmem)])

        super().__init__(self.device_name, self.name)

    def __repr__(self):
        return f'{self.device_name}{self.naddr}to{self.nmem}({self.name}, {[self.A[i].value for i in range(self.naddr)]} -> {[self.O[i].value for i in range(self.nmem)]})'
    
    def set_addr(self, addr):
        if addr < 0 or addr > self.nmem - 1:
            raise(RuntimeError)

        bin = i2bi(addr, 4)
        for i in range(self.naddr):
            self.A[i].value = int(bin[i])
    
    def get_output(self):
        strO = ''
        for i in range(self.nmem):
            strO = f'{self.O[i].value}{strO}'
        O = int(strO, 2)
        return O
    
class Selector(SimulatedCircuit):
    # Signal: 1-D input signal to control output (0: not connect, 1: connect)
    # I: input
    # O: output
    def __init__(self, name, n):
        self.device_name = 'Selector'
        self.name = name

        self.naddr = n
        self.nmem = 2**n

        # create elements
        self.brn = Branch('brn')
        self.ands = [And(f'and{i}') for i in range(self.nmem)]

        # connect
        for i in range(self.nmem):
            self.brn >> self.ands[i].I[1]

        # create access points
        self.Signal = self.brn
        self.I = [self.ands[i].I[0] for i in range(self.nmem)]
        self.O = [self.ands[i].O for i in range(self.nmem)]

        # update sequence
        self.update_sequence = [self.brn]
        self.update_sequence.extend([self.ands[i] for i in range(self.nmem)])

        super().__init__(self.device_name, self.name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, Signal = {str(self.Signal.value)}, {''.join([str(self.I[i].value) for i in range(self.nmem)])[::-1]} -> {''.join([str(self.O[i].value) for i in range(self.nmem)])[::-1]})'
    
    def get_output(self):
        strO = ''
        for i in range(self.nmem):
            strO = f'{self.O[i].value}{strO}'
        O = int(strO, 2)
        return O


class Decoder4to16(Decoder):
    def __init__(self, name):
        super().__init__(name, 4)


class Selector16to1(Selector):
    def __init__(self, name):
        super().__init__(name, 4)


class TestDecoder(unittest.TestCase):
    def test_i2bi(self):
        print('test_i2bi')

        self.assertEqual(i2bi(0, 3), '000')
        self.assertEqual(i2bi(1, 3), '100')
        self.assertEqual(i2bi(7, 3), '111')
        self.assertEqual(i2bi(0, 4), '0000')
        self.assertEqual(i2bi(1, 4), '1000')
        self.assertEqual(i2bi(14, 4), '0111')

    def test_decoder4to16(self):
        print('test_decoder4to16')

        dec = Decoder4to16('dec')
        dec.power_on()
        dec.step()

        for i in range(16):
            dec.set_addr(i)
            dec.step()
            # print(f'{i:2d}: {dec.get_output():016b}')
            self.assertEqual(dec.get_output(), 1 << i)
    
    def test_selector16to1(self):
        print('test_selector16to1')

        sel = Selector16to1('sel')
        sel.power_on()
        sel.step()

        for i in range(16):
            for j in range(16):
                sel.I[j].reset()
            sel.I[i].set()

            sel.Signal.set()
            sel.step()
            # print(sel)
            self.assertEqual(sel.get_output(), 1 << i)
            sel.Signal.reset()
            sel.step()
            # print(sel)
            self.assertEqual(sel.get_output(), 0)

    def test_dec_sel_4to16to1(self):
        print('test_dec_sel_4to16to1')

        dec = Decoder4to16('dec')
        sel = Selector16to1('sel')
        for i in range(16):
            dec.O[i] >> sel.I[i]
        dec.power_on()
        sel.power_on()
        dec.step()
        sel.step()

        sel.Signal.set()
        for i in range(16):
            dec.set_addr(i)
            dec.step()
            sel.step()
            # print(f'{i:02d}: {dec.get_output():016b}  {sel.get_output():016b}')
            self.assertEqual(sel.get_output(), 1 << i)

        sel.Signal.reset()
        for i in range(16):
            dec.set_addr(i)
            dec.step()
            sel.step()
            # print(f'{i:02d}: {dec.get_output():016b}  {sel.get_output():016b}')
            self.assertEqual(sel.get_output(), 0)



if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestDecoder('test_i2bi'),
        TestDecoder('test_decoder4to16'),
        TestDecoder('test_selector16to1'),
        TestDecoder('test_dec_sel_4to16to1'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
