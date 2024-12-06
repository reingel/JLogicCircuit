import unittest
import random as rd
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Gate import TriStateBuffer
from Branch import Branch
from FlipFlop import LevelTriggeredDtypeFlipFlop
from Decoder import Decoder4to16, Selector16to1
from Util import i2b_ri


class Memory1bit(SimulatedCircuit):
    # Wrapper class of LevelTriggeredDtypeFlipFlop
    def __init__(self, name):
        self.device_name = '1-Bit Memory'
        self.name = name

        self.latch = LevelTriggeredDtypeFlipFlop('latch')
        self.update_sequence = [self.latch]
        self.W = self.latch.Clk
        self.DI = self.latch.D
        self.DO = self.latch.Q

        super().__init__(self.device_name, self.name)


class RAM16x8(SimulatedCircuit):
    # 16x8: "16 separate memories that can be selected by addr" x "width of data in/out"
    # Address: 4 bits
    # W: 1 bit
    # DI, DO: 8 bits (1 byte)
    def __init__(self, name):
        self.device_name = '16x8 RAM'

        self.naddr = 4
        self.nloc = 2**self.naddr
        self.nbus = 8

        # create elements
        self.dec = Decoder4to16('decoder')
        self.brndc = [Branch(f'brndc{j:02d}') for j in range(self.nloc)]
        self.selw = Selector16to1('selector for W')
        self.sele = Selector16to1('selector for E')

        self.brnw = [Branch(f'brnw{j:02d}') for j in range(self.nloc)]
        self.brndi = [Branch(f'brndi{i}') for i in range(self.nbus)]
        self.cell = [[Memory1bit(f'cell{j:02d}x{i}') for i in range(self.nbus)] for j in range(self.nloc)]
        self.tri = [[TriStateBuffer(f'tri{j:02d}x{i}') for i in range(self.nbus)] for j in range(self.nloc)]
        self.brne = [Branch(f'brne{j:02d}') for j in range(self.nloc)]
        self.brndo = [Branch(f'brndo{i}') for i in range(self.nbus)]

        # connect
        for j in range(self.nloc):
            self.dec.O[j] >> self.brndc[j] >> (self.selw.I[j], self.sele.I[j])
            self.selw.O[j] >> self.brnw[j]
            self.sele.O[j] >> self.brne[j]
            for i in range(self.nbus):
                self.brnw[j] >> self.cell[j][i].W
                self.brndi[i] >> self.cell[j][i].DI
                self.brne[j] >> self.tri[j][i].E
                self.cell[j][i].DO >> self.tri[j][i].I
                self.tri[j][i].O >> self.brndo[i]

        # create access points
        self.A = self.dec.A
        self.W = self.selw.Signal
        self.E = self.sele.Signal
        self.DI = self.brndi
        self.DO = self.brndo

        # update sequence
        self.update_sequence = [self.dec]
        self.update_sequence.extend([self.brndc[j] for j in range(self.nloc)])
        self.update_sequence.append(self.selw)
        self.update_sequence.append(self.sele)
        self.update_sequence.extend([self.brnw[j] for j in range(self.nloc)])
        self.update_sequence.extend([self.brndi[i] for i in range(self.nbus)])
        self.update_sequence.extend([self.brne[j] for j in range(self.nloc)])
        for j in range(self.nloc):
            self.update_sequence.extend([self.cell[j][i] for i in range(self.nbus)])
            self.update_sequence.extend([self.tri[j][i] for i in range(self.nbus)])
        self.update_sequence.extend([self.brndo[i] for i in range(self.nbus)])

        super().__init__('RAM16x8', name)
    
    def __repr__(self):
        return f'RAM16x8({self.name}, {self.print_cell()})'

    def print_cell(self):
        out = ''
        for j in range(self.nloc):
            strDO = ''
            for i in range(self.nbus):
                strDO = f'{self.cell[j][i].DO.value}{strDO}'
            DO = int(strDO, 2)
            out = f'{DO:02x}'.upper() + ('   ' if j == 8 else ' ') + out
        return out
    
    def set_addr(self, addr):
        if addr < 0 or addr > self.nloc - 1:
            raise(RuntimeError)
        bin = i2b_ri(addr, 4)
        for i in range(self.naddr):
            self.A[i].value = bin[i]
    
    def set_input(self, DI: int):
        if DI < 0 or DI > 2**self.nbus - 1:
            raise(RuntimeError)
        strDI = i2b_ri(DI, 8)
        for i in range(self.nbus):
            self.DI[i].value = strDI[i]
    
    def get_output(self):
        strDO = ''
        for i in range(self.nbus):
            strDO = f'{self.DO[i].value}{strDO}'
        DO = int(strDO, 2)
        return DO


class RAMnx8(SimulatedCircuit):
    # nx8: "n separate memories that can be selected by addr" x "width of data in/out"
    # Address: 4 bits
    # W: 1 bit
    # DI, DO: 8 bits (1 byte)
    def __init__(self, name, base_ram, base_ram_naddr):
        self.device_name = 'RAMnx8'
        self.name = name
        self.base_ram = globals()[base_ram] # get class from string

        self.naddr1 = base_ram_naddr # A0 ~ A3, naddr of base_ram
        self.naddr2 = 4 # A4 ~ A7, added by self.dec
        self.naddr = self.naddr1 + self.naddr2
        self.nloc = 2**self.naddr
        self.nbus = 8

        # create elements
        self.brna = [Branch(f'brna{a}') for a in range(self.naddr1)]
        self.dec = Decoder4to16('decoder')
        self.brndc = [Branch(f'brndc{j:02d}') for j in range(self.dec.nloc)]
        self.selw = Selector16to1('selector for W')
        self.sele = Selector16to1('selector for E')

        self.brndi = [Branch(f'brndi{i}') for i in range(self.nbus)]
        self.cell = [self.base_ram(f'base_ram_{j:02d}') for j in range(self.dec.nloc)]
        self.brndo = [Branch(f'brndo{i}') for i in range(self.nbus)]

        # connect
        for i in range(self.naddr1):
            for j in range(self.dec.nloc):
                self.brna[i] >> self.cell[j].A[i]
        for j in range(self.dec.nloc):
            self.dec.O[j] >> self.brndc[j] >> (self.selw.I[j], self.sele.I[j])
            self.selw.O[j] >> self.cell[j].W
            self.sele.O[j] >> self.cell[j].E
            for i in range(self.nbus):
                self.brndi[i] >> self.cell[j].DI[i]
                self.cell[j].DO[i] >> self.brndo[i]

        # create access points
        self.A = [self.brna[i] for i in range(self.naddr1)] + [self.dec.A[i] for i in range(self.naddr2)]
        self.W = self.selw.Signal
        self.E = self.sele.Signal
        self.DI = self.brndi
        self.DO = self.brndo

        # update sequence
        self.update_sequence = [self.brna[a] for a in range(self.naddr1)]
        self.update_sequence.append(self.dec)
        self.update_sequence.extend([self.brndc[j] for j in range(self.dec.nloc)])
        self.update_sequence.append(self.selw)
        self.update_sequence.append(self.sele)
        self.update_sequence.extend([self.brndi[i] for i in range(self.nbus)])
        self.update_sequence.extend([self.cell[j] for j in range(self.dec.nloc)])
        self.update_sequence.extend([self.brndo[i] for i in range(self.nbus)])

        super().__init__('RAM256x8', name)
    
    def __repr__(self):
        out = '---\n'
        for j in range(self.dec.nloc):
            out += self.cell[j].__repr__() + '\n'
        return out
        
    def set_addr(self, addr):
        if addr < 0 or addr > self.nloc - 1:
            raise(RuntimeError)
        bin = i2b_ri(addr, self.naddr)
        for i in range(self.naddr):
            self.A[i].value = bin[i]
    
    def set_input(self, DI: int):
        if DI < 0 or DI > 2**self.nbus - 1:
            raise(RuntimeError)
        strDI = i2b_ri(DI, self.nbus)
        for i in range(self.nbus):
            self.DI[i].value = strDI[i]
    
    def get_output(self):
        strDO = ''
        for i in range(self.nbus):
            strDO = f'{self.DO[i].value}{strDO}'
        DO = int(strDO, 2)
        return DO


class RAM256x8(RAMnx8):
    def __init__(self, name):
        super().__init__(name, 'RAM16x8', 4)

class RAM4096x8(RAMnx8):
    def __init__(self, name):
        super().__init__(name, 'RAM256x8', 8)


class TestMemory(unittest.TestCase):
    def test_memory1(self):
        print('test_memory1')

        dev = Memory1bit('memory1b')
        dev.power_on()
        dev.step()

        io = [ # [[DI, W], DO],
            [[1, 0], 0],
            [[1, 1], 1],
            [[1, 0], 1],
            [[0, 1], 0],
            [[0, 0], 0],
        ]

        for i in range(len(io)):
            dev.DI.value = io[i][0][0]
            dev.W.value = io[i][0][1]
            dev.step()
            self.assertEqual(dev.DO.value, io[i][1])

    def _test_ram(self, dev, nloc, ntrial=0):
        io = [ # [[DI, W, E], DO],
            [[0xFF, 0, 0], 0],
            [[0xFF, 1, 0], 0],
            [[0xFF, 0, 0], 0],
            [[0, 0, 1], 0xFF],
            [[0, 0, 0], 0],
            [[0, 1, 0], 0],
            [[0, 0, 0], 0],
            [[0, 0, 1], 0],
            [[0, 0, 0], 0],
        ]

        if ntrial == 0:
            ntrial = nloc
            mode = 'sequential'
        else:
            mode = 'random'

        for j in range(ntrial):
            if mode == 'random':
                addr = rd.randint(0, nloc - 1)
            else:
                addr = j
            print(f'{addr}', end=' ')
            dev.set_addr(addr)
            for i in range(len(io)):
                dev.set_input(io[i][0][0])
                dev.W.value = io[i][0][1]
                dev.E.value = io[i][0][2]
                dev.step()
                # print(f'{j}, DI = {io[i][0][0]:02X}, W = {io[i][0][1]}, E = {io[i][0][2]}, DO = {dev.get_output():02X}, DOreq = {io[i][1]:02X}')
                self.assertEqual(dev.get_output(), io[i][1])
        print('\n')

    def test_ram16x8(self):
        print('test_ram16x8')

        dev = RAM16x8('ram16x8')
        dev.power_on()
        dev.step()
        self._test_ram(dev, 16)

    def test_ram256x8(self):
        print('test_ram256x8')

        dev = RAM256x8('ram256x8')
        dev.power_on()
        dev.step()
        self._test_ram(dev, 256, 4)

    def test_ram4096x8(self):
        print('test_ram4096x8')

        dev = RAM4096x8('ram4096x8')
        dev.power_on()
        dev.step()
        self._test_ram(dev, 4096, 1)




if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestMemory('test_memory1'),
        TestMemory('test_ram16x8'),
        TestMemory('test_ram256x8'),
        TestMemory('test_ram4096x8'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
