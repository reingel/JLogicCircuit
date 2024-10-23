import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Junction import Split, Split8
from Gate import And4, OrN, Inverter
from FlipFlop import LevelTriggeredDtypeFlipFlop

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
        self.and4 = [And4(f'and4{i}') for i in range(self.nbit)]
        
        # connect
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
        self.I = [self.and4[i].in1 for i in range(self.nbit)]
        self.S = [self.spls[i][0].in1 for i in range(self.naddr)]
        self.O = [self.and4[i].out for i in range(self.nbit)]

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
            self.split8.out[i] >> self.latches[i].W
            # create access ports
            self.DI.append(self.latches[i].DI)
            self.DO.append(self.latches[i].DO)
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
            self.splits[i].out1 >> self.decoder.S[i]
            self.splits[i].out2 >> self.selector.S[i]
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
            self.split8.out[i] >> self.memories[i].DI
            self.memories[i].DO >> self.selector.I[i]
            # update sequences
            self.update_sequence.append(self.memories[i])
        
        self.update_sequence.append(self.selector)
        
        self.S = [self.splits[i].in1 for i in range(self.naddr)]
        self.W = self.decoder.W
        self.DI = self.split8.in1
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
                self.split8s[j].out[i] >> self.ram8x1[i].S[j]
            self.split8w.out[i] >> self.ram8x1[i].W
            
        self.update_sequence = [self.split8s[i] for i in range(self.naddr)]
        self.update_sequence.append(self.split8w)
        self.update_sequence.extend([self.ram8x1[i] for i in range(self.nmem)])
        
        self.S = [self.split8s[i].in1 for i in range(self.naddr)]
        self.W = self.split8w.in1
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



class TestFlipFlop(unittest.TestCase):
    # def test_module3to8(self):
    #     print('test_module3to8')

    #     dec = Module3to8('mod')
    #     dec.power_on()
    #     dec.step()

    #     dec.set_input(0xF0)
    #     for i in range(8):
    #         dec.set_addr(i)
    #         dec.step()

    #         print(i, f'{dec.get_output():08b}')

    # def test_decoder3to8(self):
    #     print('test_decoder3to8')

    #     dec = Decoder3to8('dec')
    #     dec.power_on()
    #     dec.step()

    #     for i in range(8):
    #         dec.set_addr(i)
    #         dec.W.value = HIGH
    #         dec.step()
    #         print(i, f'{dec.get_output():08b}')

    # def test_selector8to1(self):
    #     print('test_selector8to1')

    #     sel = Selector8to1('sel')
    #     sel.power_on()
    #     sel.step()

    #     sel.set_input(0x0F)
    #     out = ''
    #     for i in range(8):
    #         sel.set_addr(i)
    #         sel.step()
    #         out = str(sel.get_output()) + out
    #     print(out)

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
    
    def test_ram8x8(self):
        dev = RAM8x8('ram8x8')
        dev.power_on()
        dev.step()

        for i in range(8):
            dev.set_input(0xF0)
            dev.set_addr(i)
            dev.W.value = HIGH
            dev.step()
            print(f'{dev.get_output():02x}')
            print(dev)

        print(dev)




if __name__ == '__main__':
    unittest.main()