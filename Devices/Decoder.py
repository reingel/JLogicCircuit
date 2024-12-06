import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Branch import Branch
from Gate import And, AndN, OrN, Or, Inverter
from Util import i2b_ri, pav2i


class Decoder(SimulatedCircuit):
    # W: 1 bit (Write)
    # A: Address
    # O: Output, one-hot
    def __init__(self, name, n):
        self.device_name = 'Decoder'
        self.name = name

        self.naddr = n
        self.nloc = 2**n

        # create elements
        self.brnd = [Branch(f'brnd{i}') for i in range(self.naddr)] # branch directly connected
        self.inv = [Inverter(f'inv{i}') for i in range(self.naddr)]
        self.brni = [Branch(f'brni{i}') for i in range(self.naddr)] # branch connected through inverter
        self.ando = [AndN(f'and{i}', 4) for i in range(self.nloc)]
        
        # connect
        for i in range(self.naddr):
            self.brnd[i] >> self.inv[i]
            self.inv[i] >> self.brni[i]
            for j in range(self.nloc):
                bin = i2b_ri(j, self.naddr)
                (self.brnd[i] if bin[i] == 1 else self.brni[i]) >> self.ando[j].I[i]

        # create access points
        self.A = self.brnd
        self.O = [self.ando[i].O for i in range(self.nloc)]

        # update sequences
        self.update_sequence = [self.brnd[i] for i in range(self.naddr)]
        self.update_sequence.extend([self.inv[i] for i in range(self.naddr)])
        self.update_sequence.extend([self.brni[i] for i in range(self.naddr)])
        self.update_sequence.extend([self.ando[j] for j in range(self.nloc)])

        super().__init__(self.device_name, self.name)

    def __repr__(self):
        return f'{self.device_name}{self.naddr}to{self.nloc}({self.name}, {[self.A[i].value for i in range(self.naddr)]} -> {[self.O[i].value for i in range(self.nloc)]})'
    
    def set_addr(self, addr):
        if addr < 0 or addr > self.nloc - 1:
            raise(RuntimeError)

        bin = i2b_ri(addr, 4)
        for i in range(self.naddr):
            self.A[i].value = bin[i]
    
    def get_output(self):
        return pav2i(self.O, self.nloc)
    

class Decoder4to16(Decoder):
    def __init__(self, name):
        super().__init__(name, 4)


class Selector(SimulatedCircuit):
    # Signal: 1-D input signal to control output (0: not connect, 1: connect)
    # I: input
    # O: output
    def __init__(self, name, n):
        self.device_name = 'Selector'
        self.name = name

        self.naddr = n
        self.nloc = 2**n

        # create elements
        self.brn = Branch('brn')
        self.ando = [And(f'and{i}') for i in range(self.nloc)]

        # connect
        for i in range(self.nloc):
            self.brn >> self.ando[i].I[1]

        # create access points
        self.Signal = self.brn
        self.I = [self.ando[i].I[0] for i in range(self.nloc)]
        self.O = [self.ando[i].O for i in range(self.nloc)]

        # update sequence
        self.update_sequence = [self.brn]
        self.update_sequence.extend([self.ando[i] for i in range(self.nloc)])

        super().__init__(self.device_name, self.name)
    
    def __repr__(self):
        return f"{self.device_name}({self.name}, Signal = {str(self.Signal.value)}, {''.join([str(self.I[i].value) for i in range(self.nloc)])[::-1]} -> {''.join([str(self.O[i].value) for i in range(self.nloc)])[::-1]})"
    
    def get_output(self):
        return pav2i(self.O, self.nloc)


class Selector16to1(Selector):
    def __init__(self, name):
        super().__init__(name, 4)


class Selector2to1(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'Selector2to1'
        self.name = name

        self.brn = Branch('brn')
        self.inv = Inverter('inv')
        self.andA = And('andA')
        self.andB = And('andB')
        self.orO = Or('orO')

        self.brn >> (self.inv, self.andB.I[0])
        self.inv >> self.andA.I[1]
        self.andA.O >> self.orO.I[0]
        self.andB.O >> self.orO.I[1]

        self.Select = self.brn
        self.A = self.andA.I[0]
        self.B = self.andB.I[1]
        self.O = self.orO.O

        self.update_sequence = [self.brn, self.inv, self.andA, self.andB, self.orO]

        super().__init__(self.device_name, self.name)


class TestDecoder(unittest.TestCase):
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

    def test_selector2to1(self):
        sel = Selector2to1('sel')
        sel.power_on()

        sel.A.set()
        sel.B.reset()
        sel.Select.reset() # A -> O
        sel.step()
        self.assertEqual(sel.O.value, HIGH)
        sel.Select.set() # B -> O
        sel.step()
        self.assertEqual(sel.O.value, OPEN)

        sel.A.reset()
        sel.B.set()
        sel.Select.reset() # A -> O
        sel.step()
        self.assertEqual(sel.O.value, OPEN)
        sel.Select.set() # B -> O
        sel.step()
        self.assertEqual(sel.O.value, HIGH)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestDecoder('test_decoder4to16'),
        TestDecoder('test_selector16to1'),
        TestDecoder('test_dec_sel_4to16to1'),
        TestDecoder('test_selector2to1'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
