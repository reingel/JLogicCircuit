import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Branch import Branch
from Gate import And, AndN, OrN, Inverter

class Module3to8(SimulatedCircuit):
    # pass through only one signal selelcted by address
    # I: I0 - I7 (Input)
    # S: S0 - S2 (Address)
    # O: O0 - O7 (Output)
    def __init__(self, name):
        self.name = name

        self.naddr = 3
        self.nbit = 8

        # create elements
        self.spls = [[Branch(f'spls{i}{j}') for j in range(4)] for i in range(self.naddr)]
        self.inv = [Inverter(f'inv{i}') for i in range(self.naddr)]
        self.spln = [[Branch(f'spln{i}{j}') for j in range(3)] for i in range(self.naddr)]
        self.and4 = [AndN(f'and4{i}', 4) for i in range(self.nbit)]
        
        # connect
        self.spls[0][0] >> self.spls[0][1]
        self.spls[0][0] >> self.inv[0].I
        self.spls[0][1] >> self.spls[0][2]
        self.spls[0][1] >> self.and4[7].I[1]
        self.spls[0][2] >> self.spls[0][3]
        self.spls[0][2] >> self.and4[5].I[1]
        self.spls[0][3] >> self.and4[1].I[1]
        self.spls[0][3] >> self.and4[3].I[1]

        self.spls[1][0] >> self.spls[1][1]
        self.spls[1][0] >> self.inv[1].I
        self.spls[1][1] >> self.spls[1][2]
        self.spls[1][1] >> self.and4[7].I[2]
        self.spls[1][2] >> self.spls[1][3]
        self.spls[1][2] >> self.and4[6].I[2]
        self.spls[1][3] >> self.and4[2].I[2]
        self.spls[1][3] >> self.and4[3].I[2]

        self.spls[2][0] >> self.spls[2][1]
        self.spls[2][0] >> self.inv[2].I
        self.spls[2][1] >> self.spls[2][2]
        self.spls[2][1] >> self.and4[7].I[3]
        self.spls[2][2] >> self.spls[2][3]
        self.spls[2][2] >> self.and4[6].I[3]
        self.spls[2][3] >> self.and4[4].I[3]
        self.spls[2][3] >> self.and4[5].I[3]

        self.inv[0].O >> self.spln[0][0]
        self.spln[0][0] >> self.spln[0][1]
        self.spln[0][0] >> self.and4[6].I[1]
        self.spln[0][1] >> self.spln[0][2]
        self.spln[0][1] >> self.and4[4].I[1]
        self.spln[0][2] >> self.and4[0].I[1]
        self.spln[0][2] >> self.and4[2].I[1]

        self.inv[1].O >> self.spln[1][0]
        self.spln[1][0] >> self.spln[1][1]
        self.spln[1][0] >> self.and4[5].I[2]
        self.spln[1][1] >> self.spln[1][2]
        self.spln[1][1] >> self.and4[4].I[2]
        self.spln[1][2] >> self.and4[0].I[2]
        self.spln[1][2] >> self.and4[1].I[2]

        self.inv[2].O >> self.spln[2][0]
        self.spln[2][0] >> self.spln[2][1]
        self.spln[2][0] >> self.and4[3].I[3]
        self.spln[2][1] >> self.spln[2][2]
        self.spln[2][1] >> self.and4[2].I[3]
        self.spln[2][2] >> self.and4[0].I[3]
        self.spln[2][2] >> self.and4[1].I[3]

        # create access points
        self.I = [self.and4[i].I[0] for i in range(self.nbit)]
        self.S = [self.spls[i][0] for i in range(self.naddr)]
        self.O = [self.and4[i].O for i in range(self.nbit)]

        # update sequences
        self.update_sequence = []
        for i in range(self.naddr):
            for j in range(4):
                self.update_sequence.append(self.spls[i][j])
        for i in range(self.naddr):
            self.update_sequence.append(self.inv[i])
            for j in range(3):
                self.update_sequence.append(self.spln[i][j])
        for i in range(self.nbit):
            self.update_sequence.append(self.and4[i])

        super().__init__('Module3to8', name)

    def __repr__(self):
        return f'Module3to8({self.name}, I={[self.I[i].value for i in range(self.nbit)]}, S={[self.S[i].value for i in range(self.naddr)]} -> O={[self.O[i].value for i in range(self.nbit)]})'

    def set_input(self, DI: int):
        if DI > 255 or DI < 0:
            raise(RuntimeError)
        strDI = f'{DI:08b}'[::-1]
        for i in range(self.nbit):
            self.I[i].value = int(strDI[i])
    
    def set_addr(self, addr):
        if addr < 0 or addr > 7:
            raise(RuntimeError)

        bin = f'{addr:03b}'[::-1]
        for i in range(self.naddr):
            self.S[i].value = int(bin[i])
    
    def get_output(self):
        strO = ''
        for i in range(self.nbit):
            strO = f'{self.O[i].value}{strO}'
        O = int(strO, 2)
        return O


class Decoder3to8(SimulatedCircuit):
    # W: 1 bit (Write)
    # S: S0 - S2 (Address)
    # O: O0 - O7 (Output, one-hot)
    def __init__(self, name):
        self.name = name

        self.naddr = 3
        self.nbit = 8

        # create elements
        self.brnw = [Branch(f'brnw{i}') for i in range(self.nbit - 1)]
        self.module = Module3to8('module')
        
        # connect
        for i in range(self.nbit - 2):
            self.brnw[i] >> self.brnw[i+1]
            self.brnw[i] >> self.module.I[i]
        self.brnw[self.nbit - 2] >> self.module.I[self.nbit - 1]
        self.brnw[self.nbit - 2] >> self.module.I[self.nbit - 2]

        # create access points
        self.W = self.brnw[0]
        self.S = [self.module.S[i] for i in range(self.naddr)]
        self.O = [self.module.O[i] for i in range(self.nbit)]

        # update sequences
        self.update_sequence = [self.brnw[i] for i in range(self.nbit - 1)]
        self.update_sequence.append(self.module)

        super().__init__('Decoder3to8', name)

    def __repr__(self):
        return f'Decoder3to8({self.name}, W={self.W.value}, S={[self.S[i].value for i in range(self.naddr)]} -> O={[self.O[i].value for i in range(self.nbit)]})'
    
    def set_addr(self, addr):
        if addr < 0 or addr > 7:
            raise(RuntimeError)

        bin = f'{addr:03b}'[::-1]
        for i in range(self.naddr):
            self.S[i].value = int(bin[i])
    
    def get_output(self):
        strO = ''
        for i in range(self.nbit):
            strO = f'{self.O[i].value}{strO}'
        O = int(strO, 2)
        return O


class Selector8to1(SimulatedCircuit):
    # I: I0 - I7 (Input)
    # S: S0 - S2 (Address)
    # DO: 1 bit
    def __init__(self, name):
        self.name = name

        self.naddr = 3
        self.nbit = 8

        # create elements
        self.module = Module3to8('module')
        self.or8 = OrN('or8', self.nbit)
        
        # connect
        for i in range(self.nbit):
            self.module.O[i] >> self.or8.I[i]

        # create access points
        self.I = [self.module.I[i] for i in range(self.nbit)]
        self.S = [self.module.S[i] for i in range(self.naddr)]
        self.DO = self.or8.O

        # update sequences
        self.update_sequence = [self.module, self.or8]

        super().__init__('Selector8to1', name)

    def __repr__(self):
        return f'Selector8to1({self.name}, I={[self.I[i].value for i in range(self.nbit)]}, S={[self.S[i].value for i in range(self.naddr)]} -> O={self.DO.value})'
    
    def set_input(self, DI: int):
        if DI > 255 or DI < 0:
            raise(RuntimeError)
        strDI = f'{DI:08b}'[::-1]
        for i in range(self.nbit):
            self.I[i].value = int(strDI[i])
    
    def set_addr(self, addr):
        if addr < 0 or addr > 7:
            raise(RuntimeError)

        bin = f'{addr:03b}'[::-1]
        for i in range(self.naddr):
            self.S[i].value = int(bin[i])
    
    def get_output(self):
        return self.DO.value


class Decoder4to16(SimulatedCircuit):
    # A: A0 - A3  (Address)
    # O: O0 - O15 (Output, one-hot)
    def __init__(self, name):
        self.name = name

        self.naddr = 4
        self.nmem = 2**self.naddr

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
                bin = f'{j:04b}'[::-1]
                (self.brnd[i] if bin[i] == '1' else self.brni[i]) >> self.ando[j].I[i]

        # create access points
        self.A = self.brnd
        self.O = [self.ando[i].O for i in range(self.nmem)]

        # update sequences
        self.update_sequence = [self.brnd[i] for i in range(self.naddr)]
        self.update_sequence.extend([self.inv[i] for i in range(self.naddr)])
        self.update_sequence.extend([self.brni[i] for i in range(self.naddr)])
        self.update_sequence.extend([self.ando[j] for j in range(self.nmem)])

        super().__init__('Decoder4to16', self.name)

    def __repr__(self):
        return f'Decoder4to16({self.name}, {[self.A[i].value for i in range(self.naddr)]} -> {[self.O[i].value for i in range(self.nmem)]})'
    
    def set_addr(self, addr):
        if addr < 0 or addr > self.nmem - 1:
            raise(RuntimeError)

        bin = f'{addr:04b}'[::-1]
        for i in range(self.naddr):
            self.A[i].value = int(bin[i])
    
    def get_output(self):
        strO = ''
        for i in range(self.nmem):
            strO = f'{self.O[i].value}{strO}'
        O = int(strO, 2)
        return O
    
class Selector16to1(SimulatedCircuit):
    # Signal: 1-D input signal to control output (0: not connect, 1: connect)
    # I: input
    # O: output
    def __init__(self, name):
        self.name = name

        self.nmem = 16

        # create elements
        self.brn = Branch('brn')
        self.ands = [And(f'and{i:02d}') for i in range(self.nmem)]

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

        super().__init__('Selector16to1', self.name)
    
    def __repr__(self):
        return f'Selector16to1({self.name}, Signal = {str(self.Signal.value)}, {''.join([str(self.I[i].value) for i in range(self.nmem)])[::-1]} -> {''.join([str(self.O[i].value) for i in range(self.nmem)])[::-1]})'
    
    def get_output(self):
        strO = ''
        for i in range(self.nmem):
            strO = f'{self.O[i].value}{strO}'
        O = int(strO, 2)
        return O
    

class TestDecoder(unittest.TestCase):
    def test_module3to8(self):
        print('test_module3to8')

        dec = Module3to8('mod')
        dec.power_on()
        dec.step()

        inp = 0xAA
        dec.set_input(inp)
        for i in range(8):
            dec.set_addr(i)
            dec.step()
            # print(i, f'{dec.get_output():08b}')
            self.assertEqual(dec.get_output() & (1 << i), inp & (1 << i))

    def test_decoder3to8(self):
        print('test_decoder3to8')

        dec = Decoder3to8('dec')
        dec.power_on()
        dec.step()

        dec.W.set()
        for i in range(8):
            dec.set_addr(i)
            dec.step()
            # print(i, f'{dec.get_output():08b}')
            self.assertEqual(dec.get_output() & (1 << i), 1 << i)

        dec.W.reset()
        for i in range(8):
            dec.set_addr(i)
            dec.step()
            # print(i, f'{dec.get_output():08b}')
            self.assertEqual(dec.get_output() & (1 << i), 0)

    def test_selector8to1(self):
        print('test_selector8to1')

        sel = Selector8to1('sel')
        sel.power_on()
        sel.step()

        inp = 0xAA
        sel.set_input(inp)
        # out = ''
        for i in range(8):
            sel.set_addr(i)
            sel.step()
            # out = str(sel.get_output()) + out
            self.assertEqual(sel.get_output(), (inp >> i) & 1)
        # print(out)
    
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
        TestDecoder('test_module3to8'),
        TestDecoder('test_decoder3to8'),
        TestDecoder('test_selector8to1'),
        TestDecoder('test_decoder4to16'),
        TestDecoder('test_selector16to1'),
        TestDecoder('test_dec_sel_4to16to1'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
