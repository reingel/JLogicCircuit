import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Gate import And, Or, Inverter
from Junction import Split, Split8
from FlipFlop import LevelTriggeredDtypeFlipFlop
from Decoder import Decoder3to8, Selector8to1


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
        self.split8 = Split8('split8')
        self.latches = []
        self.DI = []
        self.DO = []

        self.update_sequence = [self.split8]

        for i in range(self.nbit):
            # create elements
            latch = Memory1bit(f'latch{i:02d}')
            self.latches.append(latch)
            # connect
            self.split8.O[i] >> self.latches[i].W
            # create access ports
            self.DI.append(self.latches[i].DI)
            self.DO.append(self.latches[i].DO)
            # update sequences
            self.update_sequence.append(self.latches[i])
        
        self.W = self.split8.I

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
        self.splits = []
        self.decoder = Decoder3to8('3-to-8 decoder')
        self.split8 = Split8('split8')
        self.memories = []
        self.selector = Selector8to1('8-to-1 selector')

        self.update_sequence = []

        for i in range(self.naddr):
            # create elements
            split = Split(f'S{i}')
            self.splits.append(split)
            # connect
            self.splits[i].O0 >> self.decoder.S[i]
            self.splits[i].O1 >> self.selector.S[i]
            # update sequences
            self.update_sequence.append(self.splits[i])
            
        self.update_sequence.append(self.decoder)
        self.update_sequence.append(self.split8)

        for i in range(self.nbit):
            # create elements
            memory = Memory1bit(f'memory{i:02d}')
            self.memories.append(memory)
            # connect
            self.decoder.O[i] >> self.memories[i].W
            self.split8.O[i] >> self.memories[i].DI
            self.memories[i].DO >> self.selector.I[i]
            # update sequences
            self.update_sequence.append(self.memories[i])
        
        self.update_sequence.append(self.selector)
        
        self.S = [self.splits[i].I for i in range(self.naddr)]
        self.W = self.decoder.W
        self.DI = self.split8.I
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

        self.split8s = [Split8(f'split8s{i}') for i in range(self.naddr)]
        self.split8w = Split8('split8w')
        self.ram8x1 = [RAM8x1(f'ram8x1_{i}') for i in range(self.nmem)]

        for i in range(self.nmem):
            # connect
            for j in range(self.naddr):
                self.split8s[j].O[i] >> self.ram8x1[i].S[j]
            self.split8w.O[i] >> self.ram8x1[i].W
            
        self.update_sequence = [self.split8s[i] for i in range(self.naddr)]
        self.update_sequence.append(self.split8w)
        self.update_sequence.extend([self.ram8x1[i] for i in range(self.nmem)])
        
        self.S = [self.split8s[i].I for i in range(self.naddr)]
        self.W = self.split8w.I
        self.DI = [self.ram8x1[i].DI for i in range(self.nmem)]
        self.DO = [self.ram8x1[i].DO for i in range(self.nmem)]

        super().__init__('RAM8x8', name)
    
    def __repr__(self):
        out = ''
        for i in range(self.nbus):
            o = ''
            for j in range(self.nmem):
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
        for i in range(self.nmem):
            self.DI[i].value = int(strDI[i])
    
    def get_output(self):
        strDO = ''
        for i in range(self.nmem):
            strDO = f'{self.DO[i].value}{strDO}'
        DO = int(strDO, 2)
        return DO


class RAM16x8(SimulatedCircuit): # implemented by adding two RAM8x8
    # 16x8: "16 separate memories that can be selected by addr" x "width of data in/out"
    # Address: 4 bits
    # W: 1 bit
    # DI, DO: 8 bits (1 byte)
    def __init__(self, name):
        self.device_name = '16x8 RAM'

        self.nram8 = 2
        self.naddr = 4
        self.nmem = 2**self.naddr
        self.nbus = 8

        self.splitA = [Split(f'splitA{i}') for i in range(self.naddr)]
        self.and2 = [And(f'and{i}') for i in range(self.nram8)]
        self.inv = Inverter('inv')
        self.splitW = Split('splitW')
        self.splitDI = [Split(f'splitDI{i}') for i in range(self.nbus)]
        self.ram8x8 = [RAM8x8(f'ram8x8_{i}') for i in range(self.nram8)]
        self.or8 = [Or(f'or{i}') for i in range(self.nbus)]

        for i in range(self.naddr - 1):
            self.splitA[i].O0 >> self.ram8x8[0].S[i]
            self.splitA[i].O1 >> self.ram8x8[1].S[i]
        self.splitA[3].O0 >> self.inv.I
        self.splitA[3].O1 >> self.and2[1].I1
        self.inv.O >> self.and2[0].I0
        self.splitW.O0 >> self.and2[0].I1
        self.splitW.O1 >> self.and2[1].I0
        for i in range(self.nram8):
            self.and2[i].O >> self.ram8x8[i].W
        for i in range(self.nbus):
            self.splitDI[i].O0 >> self.ram8x8[0].DI[i]
            self.splitDI[i].O1 >> self.ram8x8[1].DI[i]
            self.ram8x8[0].DO[i] >> self.or8[i].I0
            self.ram8x8[1].DO[i] >> self.or8[i].I1

        self.update_sequence = [self.splitA[i] for i in range(self.naddr)]
        self.update_sequence.append(self.inv)
        self.update_sequence.append(self.splitW)
        self.update_sequence.extend([self.splitDI[i] for i in range(self.nbus)])
        self.update_sequence.extend([self.and2[i] for i in range(self.nram8)])
        self.update_sequence.extend([self.ram8x8[i] for i in range(self.nram8)])
        self.update_sequence.extend([self.or8[i] for i in range(self.nbus)])
        
        self.A = [self.splitA[i].I for i in range(self.naddr)]
        self.W = self.splitW.I
        self.DI = [self.splitDI[i].I for i in range(self.nbus)]
        self.DO = [self.or8[i].O for i in range(self.nbus)]

        super().__init__('RAM16x8', name)
    
    def __repr__(self):
        out = ''
        for i in range(self.nram8):
            out = self.ram8x8[i].__repr__() + '  ' + out
        return out
        
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



class TestFlipFlop(unittest.TestCase):
    # def test_memory1(self):
    #     dev = Memory1bit('memory1b')
    #     dev.power_on()
    #     dev.step()

    #     dev.DI.value = HIGH
    #     dev.step()
    #     print(dev.DO.value)
    #     dev.W.value = HIGH
    #     dev.step()
    #     print(dev.DO.value)
    #     dev.W.value = OPEN
    #     dev.step()
    #     print(dev.DO.value)
    #     dev.DI.value = OPEN
    #     dev.W.value = HIGH
    #     dev.step()
    #     print(dev.DO.value)
    #     dev.W.value = OPEN
    #     dev.step()
    #     print(dev.DO.value)

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

    # def test_ram8x1(self):
    #     dev = RAM8x1('ram8x1')
    #     dev.power_on()
    #     dev.step()

    #     dev.DI.value = HIGH
    #     for i in range(8):
    #         dev.set_addr(i)
    #         dev.W.value = HIGH
    #         dev.step()
    #         print(dev)
    
    # def test_ram8x8(self):
    #     dev = RAM8x8('ram8x8')
    #     dev.power_on()
    #     dev.step()

    #     for i in range(8):
    #         dev.set_input(0xF0)
    #         dev.set_addr(i)
    #         dev.W.value = HIGH
    #         dev.step()
    #         print(dev)

    def test_ram16x8(self):
        dev = RAM16x8('ram16x8')
        dev.power_on()
        dev.step()

        for i in range(16):
            dev.set_input(0xF0)
            dev.set_addr(i)
            dev.W.value = HIGH
            dev.step()
            print(dev)




if __name__ == '__main__':
    unittest.main()