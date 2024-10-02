import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Junction import Split, Split8
from Gate import And4, Inverter
from FlipFlop import LevelTriggeredDtypeFlipFlip


class Decoder3to8(SimulatedCircuit):
    def __init__(self, name):
        self.name = name

        self.ni = 3
        self.no = 8

        # create elements
        self.splw = [Split(f'splw{i}') for i in range(self.no - 1)]
        self.spls = [[Split(f'spls{i}{j}') for j in range(4)] for i in range(self.ni)]
        self.inv = [Inverter(f'inv{i}') for i in range(self.ni)]
        self.spln = [[Split(f'spln{i}{j}') for j in range(3)] for i in range(self.ni)]
        self.and4 = [And4(f'and4{i}') for i in range(self.no)]
        
        # connect
        for i in range(self.no - 2):
            self.splw[i].out1 >> self.splw[i+1].in1
            self.splw[i].out2 >> self.and4[i].in1
        self.splw[self.no - 2].out1 >> self.and4[self.no - 1].in1
        self.splw[self.no - 2].out2 >> self.and4[self.no - 2].in1

        self.spls[0][0].out1 >> self.spls[0][1].in1
        self.spls[0][0].out2 >> self.inv[0].in1
        self.spls[0][1].out1 >> self.spls[0][2].in1
        self.spls[0][1].out2 >> self.and4[7].in2
        self.spls[0][2].out1 >> self.spls[0][3].in1
        self.spls[0][2].out2 >> self.and4[5].in2
        self.spls[0][3].out1 >> self.and4[1].in2
        self.spls[0][3].out2 >> self.and4[3].in2

        self.spls[1][0].out1 >> self.spls[1][1].in1
        self.spls[1][0].out2 >> self.inv[1].in1
        self.spls[1][1].out1 >> self.spls[1][2].in1
        self.spls[1][1].out2 >> self.and4[7].in3
        self.spls[1][2].out1 >> self.spls[1][3].in1
        self.spls[1][2].out2 >> self.and4[6].in3
        self.spls[1][3].out1 >> self.and4[2].in3
        self.spls[1][3].out2 >> self.and4[3].in3

        self.spls[2][0].out1 >> self.spls[2][1].in1
        self.spls[2][0].out2 >> self.inv[2].in1
        self.spls[2][1].out1 >> self.spls[2][2].in1
        self.spls[2][1].out2 >> self.and4[7].in4
        self.spls[2][2].out1 >> self.spls[2][3].in1
        self.spls[2][2].out2 >> self.and4[6].in4
        self.spls[2][3].out1 >> self.and4[4].in4
        self.spls[2][3].out2 >> self.and4[5].in4

        self.inv[0].out >> self.spln[0][0].in1
        self.spln[0][0].out1 >> self.spln[0][1].in1
        self.spln[0][0].out2 >> self.and4[6].in2
        self.spln[0][1].out1 >> self.spln[0][2].in1
        self.spln[0][1].out2 >> self.and4[4].in2
        self.spln[0][2].out1 >> self.and4[0].in2
        self.spln[0][2].out2 >> self.and4[2].in2

        self.inv[1].out >> self.spln[1][0].in1
        self.spln[1][0].out1 >> self.spln[1][1].in1
        self.spln[1][0].out2 >> self.and4[5].in3
        self.spln[1][1].out1 >> self.spln[1][2].in1
        self.spln[1][1].out2 >> self.and4[4].in3
        self.spln[1][2].out1 >> self.and4[0].in3
        self.spln[1][2].out2 >> self.and4[1].in3

        self.inv[2].out >> self.spln[2][0].in1
        self.spln[2][0].out1 >> self.spln[2][1].in1
        self.spln[2][0].out2 >> self.and4[3].in4
        self.spln[2][1].out1 >> self.spln[2][2].in1
        self.spln[2][1].out2 >> self.and4[2].in4
        self.spln[2][2].out1 >> self.and4[0].in4
        self.spln[2][2].out2 >> self.and4[1].in4

        # create access points
        self.W = self.splw[0].in1
        self.S = [self.spls[i][0].in1 for i in range(self.ni)]
        self.O = [self.and4[i].out for i in range(self.no)]

        # update sequences
        self.update_sequence = []
        for i in range(self.no - 1):
            self.update_sequence.append(self.splw[i])
        for i in range(self.ni):
            for j in range(4):
                self.update_sequence.append(self.spls[i][j])
        for i in range(self.ni):
            self.update_sequence.append(self.inv[i])
            for j in range(3):
                self.update_sequence.append(self.spln[i][j])
        for i in range(self.no):
            self.update_sequence.append(self.and4[i])

        super().__init__('Decoder3to8', name)

    def __repr__(self):
        return f'Decoder3to8({self.name}, W={self.W.value}, S={[self.S[i].value for i in range(self.ni)]} -> O={[self.O[i].value for i in range(self.no)]})'
    
    def set_addr(self, addr):
        if addr < 0 or addr > 7:
            raise(RuntimeError)

        bin = f'{addr:03b}'[::-1]
        for i in range(self.ni):
            self.S[i].value = int(bin[i])
    
    def get_output(self):
        strO = ''
        for i in range(self.no):
            strO = f'{self.O[i].value}{strO}'
        O = int(strO, 2)
        return O


class Memory8bit(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = '8-Bit Memory'

        self.nbit = 8
        self.split8 = Split8('split8')
        self.latches = []
        self.DI = []
        self.DO = []

        self.update_sequence = [self.split8]

        for i in range(self.nbit):
            # create elements
            latch = LevelTriggeredDtypeFlipFlip(f'latch{i:02d}')
            self.latches.append(latch)
            # connect
            self.split8.out[i] >> self.latches[i].Clk
            # create access ports
            self.DI.append(self.latches[i].D)
            self.DO.append(self.latches[i].Q)
            # update sequences
            self.update_sequence.append(self.latches[i])
        
        self.W = self.split8.in1

        super().__init__('Memory8bit', name)
        
    def set_input(self, DI: int):
        if DI > 255 or DI < 0:
            raise(RuntimeError)
        strDI = f'{DI:08b}'[::-1]
        for i in range(self.nbit):
            self.DI[i].value = int(strDI[i])
            a=1
    
    def get_output(self):
        strDO = ''
        for i in range(self.nbit):
            strDO = f'{self.DO[i].value}{strDO}'
        DO = int(strDO, 2)
        return DO


class TestFlipFlop(unittest.TestCase):
    # def test_memory8(self):
    #     dev = Memory8bit('memory8b')
    #     dev.power_on()
    #     dev.step()
    #     print(dev)

    #     dev.set_input(35)
    #     dev.step()
    #     DO = dev.get_output()
    #     print(DO)
    #     dev.W.value = HIGH
    #     dev.step()
    #     DO = dev.get_output()
    #     print(DO)
    #     dev.W.value = OPEN
    #     dev.step()
    #     DO = dev.get_output()
    #     print(DO)
    
    def test_decode3to8(self):
        dec = Decoder3to8('dec')
        dec.power_on()
        dec.step()

        for i in range(8):
            dec.set_addr(i)
            dec.W.value = HIGH
            dec.step()
            print(i, f'{dec.get_output():08b}')





if __name__ == '__main__':
    unittest.main()