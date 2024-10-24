import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Junction import Split, Split8
from Gate import AndN, OrN, Inverter

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
        self.spls = [[Split(f'spls{i}{j}') for j in range(4)] for i in range(self.naddr)]
        self.inv = [Inverter(f'inv{i}') for i in range(self.naddr)]
        self.spln = [[Split(f'spln{i}{j}') for j in range(3)] for i in range(self.naddr)]
        self.and4 = [AndN(f'and4{i}', 4) for i in range(self.nbit)]
        
        # connect
        self.spls[0][0].out1 >> self.spls[0][1].in1
        self.spls[0][0].out2 >> self.inv[0].in1
        self.spls[0][1].out1 >> self.spls[0][2].in1
        self.spls[0][1].out2 >> self.and4[7].I[1]
        self.spls[0][2].out1 >> self.spls[0][3].in1
        self.spls[0][2].out2 >> self.and4[5].I[1]
        self.spls[0][3].out1 >> self.and4[1].I[1]
        self.spls[0][3].out2 >> self.and4[3].I[1]

        self.spls[1][0].out1 >> self.spls[1][1].in1
        self.spls[1][0].out2 >> self.inv[1].in1
        self.spls[1][1].out1 >> self.spls[1][2].in1
        self.spls[1][1].out2 >> self.and4[7].I[2]
        self.spls[1][2].out1 >> self.spls[1][3].in1
        self.spls[1][2].out2 >> self.and4[6].I[2]
        self.spls[1][3].out1 >> self.and4[2].I[2]
        self.spls[1][3].out2 >> self.and4[3].I[2]

        self.spls[2][0].out1 >> self.spls[2][1].in1
        self.spls[2][0].out2 >> self.inv[2].in1
        self.spls[2][1].out1 >> self.spls[2][2].in1
        self.spls[2][1].out2 >> self.and4[7].I[3]
        self.spls[2][2].out1 >> self.spls[2][3].in1
        self.spls[2][2].out2 >> self.and4[6].I[3]
        self.spls[2][3].out1 >> self.and4[4].I[3]
        self.spls[2][3].out2 >> self.and4[5].I[3]

        self.inv[0].out >> self.spln[0][0].in1
        self.spln[0][0].out1 >> self.spln[0][1].in1
        self.spln[0][0].out2 >> self.and4[6].I[1]
        self.spln[0][1].out1 >> self.spln[0][2].in1
        self.spln[0][1].out2 >> self.and4[4].I[1]
        self.spln[0][2].out1 >> self.and4[0].I[1]
        self.spln[0][2].out2 >> self.and4[2].I[1]

        self.inv[1].out >> self.spln[1][0].in1
        self.spln[1][0].out1 >> self.spln[1][1].in1
        self.spln[1][0].out2 >> self.and4[5].I[2]
        self.spln[1][1].out1 >> self.spln[1][2].in1
        self.spln[1][1].out2 >> self.and4[4].I[2]
        self.spln[1][2].out1 >> self.and4[0].I[2]
        self.spln[1][2].out2 >> self.and4[1].I[2]

        self.inv[2].out >> self.spln[2][0].in1
        self.spln[2][0].out1 >> self.spln[2][1].in1
        self.spln[2][0].out2 >> self.and4[3].I[3]
        self.spln[2][1].out1 >> self.spln[2][2].in1
        self.spln[2][1].out2 >> self.and4[2].I[3]
        self.spln[2][2].out1 >> self.and4[0].I[3]
        self.spln[2][2].out2 >> self.and4[1].I[3]

        # create access points
        self.I = [self.and4[i].I[0] for i in range(self.nbit)]
        self.S = [self.spls[i][0].in1 for i in range(self.naddr)]
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
        self.splw = [Split(f'splw{i}') for i in range(self.nbit - 1)]
        self.module = Module3to8('module')
        
        # connect
        for i in range(self.nbit - 2):
            self.splw[i].out1 >> self.splw[i+1].in1
            self.splw[i].out2 >> self.module.I[i]
        self.splw[self.nbit - 2].out1 >> self.module.I[self.nbit - 1]
        self.splw[self.nbit - 2].out2 >> self.module.I[self.nbit - 2]

        # create access points
        self.W = self.splw[0].in1
        self.S = [self.module.S[i] for i in range(self.naddr)]
        self.O = [self.module.O[i] for i in range(self.nbit)]

        # update sequences
        self.update_sequence = [self.splw[i] for i in range(self.nbit - 1)]
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
        self.or8 = OrN('or8', 8)
        
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
        return f'Decoder3to8({self.name}, I={[self.I[i].value for i in range(self.nbit)]}, S={[self.S[i].value for i in range(self.naddr)]} -> O={self.DO.value})'
    
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


class TestFlipFlop(unittest.TestCase):
    def test_module3to8(self):
        print('test_module3to8')

        dec = Module3to8('mod')
        dec.power_on()
        dec.step()

        dec.set_input(0xF0)
        for i in range(8):
            dec.set_addr(i)
            dec.step()

            print(i, f'{dec.get_output():08b}')

    def test_decoder3to8(self):
        print('test_decoder3to8')

        dec = Decoder3to8('dec')
        dec.power_on()
        dec.step()

        for i in range(8):
            dec.set_addr(i)
            dec.W.value = HIGH
            dec.step()
            print(i, f'{dec.get_output():08b}')

    def test_selector8to1(self):
        print('test_selector8to1')

        sel = Selector8to1('sel')
        sel.power_on()
        sel.step()

        sel.set_input(0x0F)
        out = ''
        for i in range(8):
            sel.set_addr(i)
            sel.step()
            out = str(sel.get_output()) + out
        print(out)




if __name__ == '__main__':
    unittest.main()