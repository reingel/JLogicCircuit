import unittest
import random as rd
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Gate import TriStateBuffer
from Branch import Branch
from FlipFlop import LevelTriggeredDtypeFlipFlop
from Decoder import Decoder3to8, Selector8to1, Decoder4to16, Selector16to1


class Memory1bit(SimulatedCircuit):
    # Wrapper class of LevelTriggeredDtypeFlipFlop
    def __init__(self, name):
        self.device_name = '1-Bit Memory'

        self.latch = LevelTriggeredDtypeFlipFlop('latch')
        self.update_sequence = [self.latch]
        self.W = self.latch.Clk
        self.DI = self.latch.D
        self.DO = self.latch.Q

        super().__init__(self.device_name, name)


class Memory8bit(SimulatedCircuit):
    # W: 1 bit
    # DI, DO: 8 bits (1 byte)
    def __init__(self, name):
        self.device_name = '8-Bit Memory'

        self.nbit = 8
        self.brn = Branch('brn')
        self.latches = []
        self.DI = []
        self.DO = []

        self.update_sequence = [self.brn]

        for i in range(self.nbit):
            # create elements
            latch = Memory1bit(f'latch{i:02d}')
            self.latches.append(latch)
            # connect
            self.brn >> self.latches[i].W
            # create access ports
            self.DI.append(self.latches[i].DI)
            self.DO.append(self.latches[i].DO)
            # update sequences
            self.update_sequence.append(self.latches[i])
        
        self.W = self.brn

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

class RAM8x1(SimulatedCircuit):
    # Address: 3 bits
    # W: 1 bit
    # DI, DO: 1 bit
    def __init__(self, name):
        self.device_name = '8x1 RAM'

        self.naddr = 3
        self.nbit = 8
        self.brna = []
        self.decoder = Decoder3to8('3-to-8 decoder')
        self.brndi = Branch('brndi')
        self.memories = []
        self.selector = Selector8to1('8-to-1 selector')

        self.update_sequence = []

        for i in range(self.naddr):
            # create elements
            split = Branch(f'S{i}')
            self.brna.append(split)
            # connect
            self.brna[i] >> (self.decoder.S[i], self.selector.S[i])
            # update sequences
            self.update_sequence.append(self.brna[i])
            
        self.update_sequence.append(self.decoder)
        self.update_sequence.append(self.brndi)

        for i in range(self.nbit):
            # create elements
            memory = Memory1bit(f'memory{i:02d}')
            self.memories.append(memory)
            # connect
            self.decoder.O[i] >> self.memories[i].W
            self.brndi >> self.memories[i].DI
            self.memories[i].DO >> self.selector.I[i]
            # update sequences
            self.update_sequence.append(self.memories[i])
        
        self.update_sequence.append(self.selector)
        
        self.S = [self.brna[i] for i in range(self.naddr)]
        self.W = self.decoder.W
        self.DI = self.brndi
        self.DO = self.selector.DO

        super().__init__('RAM8x1', name)
    
    def __repr__(self):
        out = ''
        for i in range(self.nbit):
            out = str(self.memories[i].DO.value) + out
        return f'{int(out, 2):02x}'
        
    def set_addr(self, addr):
        if addr < 0 or addr > 7:
            raise(RuntimeError)

        bin = f'{addr:03b}'[::-1]
        for i in range(self.naddr):
            self.S[i].value = int(bin[i])
    
class RAM8x8(SimulatedCircuit):
    # 8x8: "8 separate memories that can be selected by addr" x "width of data in/out"
    # Address: 3 bits
    # W: 1 bit
    # DI, DO: 8 bits (1 byte)
    def __init__(self, name):
        self.device_name = '8x8 RAM'

        self.naddr = 3
        self.nmem = 2**self.naddr
        self.nbus = 8

        self.brns = [Branch(f'brns{i}') for i in range(self.naddr)]
        self.brnw = Branch('brnw')
        self.ram8x1 = [RAM8x1(f'ram8x1_{i}') for i in range(self.nbus)]

        for i in range(self.nbus):
            # connect
            for j in range(self.naddr):
                self.brns[j] >> self.ram8x1[i].S[j]
            self.brnw >> self.ram8x1[i].W
            
        self.update_sequence = [self.brns[i] for i in range(self.naddr)]
        self.update_sequence.append(self.brnw)
        self.update_sequence.extend([self.ram8x1[i] for i in range(self.nbus)])
        
        self.S = [self.brns[i] for i in range(self.naddr)]
        self.W = self.brnw
        self.DI = [self.ram8x1[i].DI for i in range(self.nbus)]
        self.DO = [self.ram8x1[i].DO for i in range(self.nbus)]

        super().__init__('RAM8x8', name)
    
    def __repr__(self):
        out = ''
        for i in range(self.nmem):
            o = ''
            for j in range(self.nbus):
                o = f'{self.ram8x1[j].memories[i].DO.value}{o}'
            t = f'{int(o, 2):02x} '.upper()
            out = t + out
        return out
        
    def set_addr(self, addr):
        if addr < 0 or addr > 7:
            raise(RuntimeError)

        bin = f'{addr:03b}'[::-1]
        for i in range(self.naddr):
            self.S[i].value = int(bin[i])
    
    def set_input(self, DI: int):
        if DI > 255 or DI < 0:
            raise(RuntimeError)
        strDI = f'{DI:08b}'[::-1]
        for i in range(self.nbus):
            self.DI[i].value = int(strDI[i])
    
    def get_output(self):
        strDO = ''
        for i in range(self.nbus):
            strDO = f'{self.DO[i].value}{strDO}'
        DO = int(strDO, 2)
        return DO


class RAM16x8(SimulatedCircuit):
    # 16x8: "16 separate memories that can be selected by addr" x "width of data in/out"
    # Address: 4 bits
    # W: 1 bit
    # DI, DO: 8 bits (1 byte)
    def __init__(self, name):
        self.device_name = '16x8 RAM'

        self.naddr = 4
        self.nmem = 2**self.naddr
        self.nbus = 8

        # create elements
        self.dec = Decoder4to16('decoder')
        self.brndc = [Branch(f'brndc{j:02d}') for j in range(self.nmem)]
        self.selw = Selector16to1('selector for W')
        self.sele = Selector16to1('selector for E')

        self.brnw = [Branch(f'brnw{j:02d}') for j in range(self.nmem)]
        self.brndi = [Branch(f'brndi{i}') for i in range(self.nbus)]
        self.cell = [[Memory1bit(f'cell{j:02d}x{i}') for i in range(self.nbus)] for j in range(self.nmem)]
        self.tri = [[TriStateBuffer(f'tri{j:02d}x{i}') for i in range(self.nbus)] for j in range(self.nmem)]
        self.brne = [Branch(f'brne{j:02d}') for j in range(self.nmem)]
        self.brndo = [Branch(f'brndo{i}') for i in range(self.nbus)]

        # connect
        for j in range(self.nmem):
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
        self.update_sequence.extend([self.brndc[j] for j in range(self.nmem)])
        self.update_sequence.append(self.selw)
        self.update_sequence.append(self.sele)
        self.update_sequence.extend([self.brnw[j] for j in range(self.nmem)])
        self.update_sequence.extend([self.brndi[i] for i in range(self.nbus)])
        self.update_sequence.extend([self.brne[j] for j in range(self.nmem)])
        for j in range(self.nmem):
            self.update_sequence.extend([self.cell[j][i] for i in range(self.nbus)])
            self.update_sequence.extend([self.tri[j][i] for i in range(self.nbus)])
        self.update_sequence.extend([self.brndo[i] for i in range(self.nbus)])

        super().__init__('RAM16x8', name)
    
    def __repr__(self):
        return f'RAM16x8({self.name})'

    def print_cell(self):
        out = ''
        for j in range(self.nmem):
            strDO = ''
            for i in range(self.nbus):
                strDO = f'{self.cell[j][i].DO.value}{strDO}'
            DO = int(strDO, 2)
            out = f'{DO:02x}'.upper() + ('   ' if j == 8 else ' ') + out
        return out
    
    def update_inport(self):
        for i in range(self.nbus):
            self.DI[i].update_value()
        
    def set_addr(self, addr):
        if addr < 0 or addr > self.nmem - 1:
            raise(RuntimeError)
        bin = f'{addr:04b}'[::-1]
        for i in range(self.naddr):
            self.A[i].value = int(bin[i])
    
    def set_input(self, DI: int):
        if DI < 0 or DI > 2**self.nbus - 1:
            raise(RuntimeError)
        strDI = f'{DI:08b}'[::-1]
        for i in range(self.nbus):
            self.DI[i].value = int(strDI[i])
    
    def get_output(self):
        strDO = ''
        for i in range(self.nbus):
            strDO = f'{self.DO[i].value}{strDO}'
        DO = int(strDO, 2)
        return DO


class RAM256x8(SimulatedCircuit):
    # 256x8: "256 separate memories that can be selected by addr" x "width of data in/out"
    # Address: 4 bits
    # W: 1 bit
    # DI, DO: 8 bits (1 byte)
    def __init__(self, name):
        self.device_name = '256x8 RAM'

        self.naddr1 = 4 # A0 ~ A3
        self.naddr2 = 4 # A4 ~ A7
        self.naddr = self.naddr1 + self.naddr2
        self.nmem = 2**self.naddr
        self.nbus = 8

        # create ports
        # self.A = [Port(f'A{a:02d}', self) for a in range(self.naddr)]
        # self.DI = [Port(f'DI{i}', self) for i in range(self.nbus)]
        # self.DO = [Port(f'DO{i}', self) for i in range(self.nbus)]
        self.A = []

        # create elements
        self.brna = [Branch(f'brna{a}') for a in range(self.naddr1)]
        self.dec = Decoder4to16('decoder')
        self.brndc = [Branch(f'brndc{j:02d}') for j in range(self.dec.nmem)]
        self.selw = Selector16to1('selector for W')
        self.sele = Selector16to1('selector for E')

        self.brndi = [Branch(f'brndi{i}') for i in range(self.nbus)]
        self.cell = [RAM16x8(f'ram16x8_{j:02d}') for j in range(self.dec.nmem)]
        self.brndo = [Branch(f'brndo{i}') for i in range(self.nbus)]

        # connect
        for a in range(self.naddr1):
            self.A.append(self.brna[a])
            for j in range(self.dec.nmem):
                self.brna[a] >> self.cell[j].A[a]
        for j in range(self.dec.nmem):
            self.dec.O[j] >> self.brndc[j] >> (self.selw.I[j], self.sele.I[j])
            self.selw.O[j] >> self.cell[j].W
            self.sele.O[j] >> self.cell[j].E
            for i in range(self.nbus):
                self.brndi[i] >> self.cell[j].DI[i]
                self.cell[j].DO[i] >> self.brndo[i]

        # create access points
        for a in range(self.naddr2):
            self.A.append(self.dec.A[a])
        self.W = self.selw.Signal
        self.E = self.sele.Signal
        self.DI = self.brndi
        self.DO = self.brndo

        # update sequence
        self.update_sequence = [self.brna[a] for a in range(self.naddr1)]
        self.update_sequence.append(self.dec)
        self.update_sequence.extend([self.brndc[j] for j in range(self.dec.nmem)])
        self.update_sequence.append(self.selw)
        self.update_sequence.append(self.sele)
        self.update_sequence.extend([self.brndi[i] for i in range(self.nbus)])
        self.update_sequence.extend([self.cell[j] for j in range(self.dec.nmem)])
        self.update_sequence.extend([self.brndo[i] for i in range(self.nbus)])

        super().__init__('RAM256x8', name)
    
    def __repr__(self):
        out = '---\n'
        for j in range(self.dec.nmem):
            out += self.cell[j].__repr__() + '\n'
            # if j % 2 == 1:
            #     out += '\n'
        return out
        
    def update_inport(self):
        for i in range(self.naddr1):
            self.A[i].update_value()
        for i in range(self.nbus):
            self.DI[i].update_value()
        
    # def step(self, n=1): # overloaded due to speed up
    #     self.update_inport()
    #     for device in self.update_sequence:
    #         if isinstance(device, RAM16x8):
    #             for j in range(self.dec.nmem):
    #                 if self.dec.O[j].value == HIGH and device == self.cell[j]:
    #                     device.step()
    #                     print(device)
    #         else:
    #             device.step()

    def set_addr(self, addr):
        if addr < 0 or addr > self.nmem - 1:
            raise(RuntimeError)
        bin = f'{addr:08b}'[::-1]
        for i in range(self.naddr):
            self.A[i].value = int(bin[i])
    
    def set_input(self, DI: int):
        if DI < 0 or DI > 2**self.nbus - 1:
            raise(RuntimeError)
        strDI = f'{DI:08b}'[::-1]
        for i in range(self.nbus):
            self.DI[i].value = int(strDI[i])
    
    def get_output(self):
        strDO = ''
        for i in range(self.nbus):
            strDO = f'{self.DO[i].value}{strDO}'
        DO = int(strDO, 2)
        return DO


class RAM4096x8(SimulatedCircuit):
    # 4096x8: "4096 separate memories that can be selected by addr" x "width of data in/out"
    # Address: 12 bits
    # W: 1 bit
    # DI, DO: 8 bits (1 byte)
    def __init__(self, name):
        self.device_name = '4096x8 RAM'

        self.naddr1 = 8 # A0 ~ A7
        self.naddr2 = 4 # A8 ~ A11
        self.naddr = self.naddr1 + self.naddr2
        self.nmem = 2**self.naddr
        self.nbus = 8

        # create ports
        self.A = []

        # create elements
        self.brna = [Branch(f'brna{a}') for a in range(self.naddr1)]
        self.dec = Decoder4to16('decoder')
        self.brndc = [Branch(f'brndc{j:02d}') for j in range(self.dec.nmem)]
        self.selw = Selector16to1('selector for W')
        self.sele = Selector16to1('selector for E')

        self.brndi = [Branch(f'brndi{i}') for i in range(self.nbus)]
        self.cell = [RAM256x8(f'ram256x8{j:02d}') for j in range(self.dec.nmem)]
        self.brndo = [Branch(f'brndo{i}') for i in range(self.nbus)]

        # connect
        for a in range(self.naddr1):
            self.A.append(self.brna[a])
            for j in range(self.dec.nmem):
                self.brna[a] >> self.cell[j].A[a]
        for j in range(self.dec.nmem):
            self.dec.O[j] >> self.brndc[j] >> (self.selw.I[j], self.sele.I[j])
            self.selw.O[j] >> self.cell[j].W
            self.sele.O[j] >> self.cell[j].E
            for i in range(self.nbus):
                self.brndi[i] >> self.cell[j].DI[i]
                self.cell[j].DO[i] >> self.brndo[i]

        # create access points
        for a in range(self.naddr2):
            self.A.append(self.dec.A[a])
        self.W = self.selw.Signal
        self.E = self.sele.Signal
        self.DI = self.brndi
        self.DO = self.brndo

        # update sequence
        self.update_sequence = [self.brna[a] for a in range(self.naddr1)]
        self.update_sequence.append(self.dec)
        self.update_sequence.extend([self.brndc[j] for j in range(self.dec.nmem)])
        self.update_sequence.append(self.selw)
        self.update_sequence.append(self.sele)
        self.update_sequence.extend([self.brndi[i] for i in range(self.nbus)])
        self.update_sequence.extend([self.cell[j] for j in range(self.dec.nmem)])
        self.update_sequence.extend([self.brndo[i] for i in range(self.nbus)])

        super().__init__('RAM4096x8', name)
    
    def __repr__(self):
        out = '---\n'
        # for j in range(self.dec.nmem):
        for j in range(2):
            out += self.cell[j].__repr__() + '\n'
        return out
        
    def update_inport(self):
        for i in range(self.naddr1):
            self.A[i].update_value()
        for i in range(self.nbus):
            self.DI[i].update_value()
        
    def set_addr(self, addr):
        if addr < 0 or addr > self.nmem - 1:
            raise(RuntimeError)
        bin = f'{addr:012b}'[::-1]
        for i in range(self.naddr):
            self.A[i].value = int(bin[i])
    
    def set_input(self, DI: int):
        if DI < 0 or DI > 2**self.nbus - 1:
            raise(RuntimeError)
        strDI = f'{DI:08b}'[::-1]
        for i in range(self.nbus):
            self.DI[i].value = int(strDI[i])
    
    def get_output(self):
        strDO = ''
        for i in range(self.nbus):
            strDO = f'{self.DO[i].value}{strDO}'
        DO = int(strDO, 2)
        return DO


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

    def test_memory8(self):
        print('test_memory8')

        dev = Memory8bit('memory8b')
        dev.power_on()
        dev.step()

        io = [ # [[DI, W], DO]
            [[35, 0], 0],
            [[35, 1], 35],
            [[35, 0], 35],
            [[12, 0], 35],
            [[12, 1], 12],
            [[12, 0], 12],
            [[0, 0], 12],
            [[0, 1], 0],
            [[0, 0], 0],
        ]

        for i in range(len(io)):
            dev.set_input(io[i][0][0])
            dev.W.value = io[i][0][1]
            dev.step()
            self.assertEqual(dev.get_output(), io[i][1])

    def test_ram8x1(self):
        print('test_ram8x1')

        nmem = 8

        dev = RAM8x1('ram8x1')
        dev.power_on()
        dev.step()
    
        io = [ # [[DI, W], DO],
            [[1, 0], 0],
            [[1, 1], 1],
            [[1, 0], 1],
            [[0, 1], 0],
            [[0, 0], 0],
        ]

        for j in range(nmem):
            dev.set_addr(j)
            for i in range(len(io)):
                dev.DI.value = io[i][0][0]
                dev.W.value = io[i][0][1]
                dev.step()
                self.assertEqual(dev.DO.value, io[i][1])
                for k in range(nmem):
                    self.assertEqual(dev.memories[k].DO.value, io[i][1] if j == k else 0)

    def test_ram8x8(self):
        print('test_ram8x8')

        nmem = 8
        nbit = 8

        dev = RAM8x8('ram8x8')
        dev.power_on()
        dev.step()

        io = [ # [[DI, W], DO],
            [[0xFF, 0], 0],
            [[0xFF, 1], 0xFF],
            [[0xFF, 0], 0xFF],
            [[0, 1], 0],
            [[0, 0], 0],
        ]

        for j in range(nmem):
            dev.set_addr(j)
            for i in range(len(io)):
                dev.set_input(io[i][0][0])
                dev.W.value = io[i][0][1]
                dev.step()
                self.assertEqual(dev.get_output(), io[i][1])

    def _test_ram(self, dev, nmem, ntrial=0):
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
            ntrial = nmem
            mode = 'sequential'
        else:
            mode = 'random'

        for j in range(ntrial):
            if mode == 'random':
                addr = rd.randint(0, nmem - 1)
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
        TestMemory('test_memory8'),
        TestMemory('test_ram8x1'),
        TestMemory('test_ram8x8'),
        TestMemory('test_ram16x8'),
        TestMemory('test_ram256x8'),
        TestMemory('test_ram4096x8'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
