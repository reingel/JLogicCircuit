import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Gate import Inverter, And, Or, OrN, TriState8bit, TriState9bit
from Branch import Branch
from Decoder import Selector2to1
from Arithmetic import Adder8bit
from Counter import Oscillator, RippleCounter4Bit
from FlipFlop import EdgeTriggeredDtypeFlipFlop, Latch8bit, Latch9bit
from Memory import RAM256x8
from Util import i2b_ri, pav2i


class Selector2to1xN(SimulatedCircuit):
    def __init__(self, name, naddr):
        self.device_name = 'Selector2to1xN'
        self.name = name

        self.naddr = naddr
        self.nbit = 8
        self.nctrl = 2 # Write, Enable
        self.n = self.naddr + self.nbit + self.nctrl

        self.brn = Branch('brn')
        self.sel = [Selector2to1(f'sel{i:02d}') for i in range(self.n)]

        self.brn >> [self.sel[i].Select for i in range(self.n)]

        self.Select = self.brn
        self.addrA = [self.sel[i].A for i in range(self.naddr)]
        self.diA = [self.sel[i + self.naddr].A for i in range(self.nbit)]
        self.wA = self.sel[self.naddr + self.nbit].A
        self.eA = self.sel[self.naddr + self.nbit + 1].A
        self.addrB = [self.sel[i].B for i in range(self.naddr)]
        self.diB = [self.sel[i + self.naddr].B for i in range(self.nbit)]
        self.wB = self.sel[self.naddr + self.nbit].B
        self.eB = self.sel[self.naddr + self.nbit + 1].B
        self.addrO = [self.sel[i].O for i in range(self.naddr)]
        self.diO = [self.sel[i + self.naddr].O for i in range(self.nbit)]
        self.wO = self.sel[self.naddr + self.nbit].O
        self.eO = self.sel[self.naddr + self.nbit + 1].O

        self.update_sequence = [self.brn]
        self.update_sequence.extend([self.sel[i] for i in range(self.n)])

        super().__init__(self.device_name, self.name)
    
    def setA(self):
        self.Select.reset()
    
    def setB(self):
        self.Select.set()
    
    def set_addrA(self, addr):
        if addr < 0 or addr > 2**self.naddr - 1:
            raise(RuntimeError)
        bin = i2b_ri(addr, self.naddr)
        for i in range(self.naddr):
            self.addrA[i].value = bin[i]
    
    def set_inputA(self, DI: int):
        if DI < 0 or DI > 2**self.nbit - 1:
            raise(RuntimeError)
        strDI = i2b_ri(DI, self.nbit)
        for i in range(self.nbit):
            self.diA[i].value = strDI[i]

    def set_addrB(self, addr):
        if addr < 0 or addr > 2**self.naddr - 1:
            raise(RuntimeError)
        bin = i2b_ri(addr, self.naddr)
        for i in range(self.naddr):
            self.addrB[i].value = bin[i]
    
    def set_inputB(self, DI: int):
        if DI < 0 or DI > 2**self.nbit - 1:
            raise(RuntimeError)
        strDI = i2b_ri(DI, self.nbit)
        for i in range(self.nbit):
            self.diB[i].value = strDI[i]

    def get_addrO(self):
        return pav2i(self.addrO, self.naddr)

    def get_inputO(self):
        return pav2i(self.diO, self.nbit)


class ControlSignal(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'ControlSignal'
        self.name = name
        self.nff = 2
        self.nbit = 8

        self.osc = Oscillator('osc')
        self.inv = Inverter('inv')
        self.brnc = Branch('brnc')
        self.brnd = Branch('brnd')
        self.brnqb = Branch('brnqb')
        self.ff = [EdgeTriggeredDtypeFlipFlop(f'ff{i}') for i in range(self.nff)]
        self.andp = And('andp')
        self.brnp = Branch('brnp')
        self.or8 = OrN('or8', self.nbit)
        self.invor = Inverter('invor') # TODO: to be combined with or8
        self.andw = And('andw')

        self.osc.O >> self.brnc >> (self.inv, self.ff[0].Clk)
        self.inv >> self.ff[1].Clk
        self.ff[0].Q >> self.brnd >> self.ff[1].D
        self.ff[0].Qbar >> self.brnqb >> (self.ff[0].D, self.andp.I[0])
        self.ff[1].Q >> self.andp.I[1]
        self.andp.O >> self.brnp >> self.andw.I[0]
        self.or8.O >> self.invor.I
        self.invor.O >> self.andw.I[1]

        self.DI = [self.or8.I[i] for i in range(self.nbit)]
        self.ToCounterClk = self.brnd
        self.ToLatchClk = self.brnp
        self.ToRamW = self.andw.O

        self.update_sequence = [self.osc, self.brnc, self.inv, self.ff[0]]
        self.update_sequence.extend([self.brnd, self.brnqb, self.ff[1], self.andp, self.brnp])
        self.update_sequence.extend([self.or8, self.invor, self.andw])

        super().__init__(self.device_name, self.name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, (ToCounterClk, ToLatchClk, ToRamW) = ({self.ToCounterClk.value}, {self.ToLatchClk.value}, {self.ToRamW.value}))'


class AccumulatingAdder(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'AccumulatingAdder'
        self.name = name
        self.nbit = 8

        self.orci = Or('orci')
        self.adder = Adder8bit('adder')
        self.brnco = Branch('brnco')
        self.brnla = [Branch(f'brnla{i}') for i in range(self.nbit)]
        self.latchH = Latch8bit('high latch')
        self.latchM = Latch9bit('mid latch')
        self.latchL = Latch9bit('low latch')
        self.triH = TriState9bit('high tri-state')
        self.triM = TriState9bit('mid tri-state')
        self.triL = TriState8bit('low tri-state')
        self.brnci = Branch('brnci')
        self.brntr = [Branch(f'brntr{i}') for i in range(self.nbit)]

        # connections for control signals
        self.orci >> self.adder.CI
        self.adder.CO >> self.brnco >> (self.latchM.D[-1], self.latchL.D[-1])
        self.latchM.Q[-1] >> self.triH.I[-1]
        self.latchL.Q[-1] >> self.triM.I[-1]
        (self.triH.O[-1], self.triM.O[-1]) >> self.brnci >> self.orci.I[1]

        # connections for data
        for i in range(self.nbit):
            self.adder.S[i] >> self.brnla[i]
            self.brnla[i] >> (self.latchH.D[i], self.latchM.D[i], self.latchL.D[i])
            self.latchH.Q[i] >> self.triH.I[i]
            self.latchM.Q[i] >> self.triM.I[i]
            self.latchL.Q[i] >> self.triL.I[i]
            (self.triH.O[i], self.triM.O[i], self.triL.O[i]) >> self.brntr[i] >> self.adder.B[i]

        self.update_sequence = [self.orci, self.adder, self.brnco]
        self.update_sequence.extend([self.brnla[i] for i in range(self.nbit)])
        self.update_sequence.extend([self.latchH, self.latchM, self.latchL])
        self.update_sequence.extend([self.triH, self.triM, self.triL])
        self.update_sequence.append(self.brnci)
        self.update_sequence.extend([self.brntr[i] for i in range(self.nbit)])

        self.A = [self.adder.A[i] for i in range(self.nbit)]
        self.CI = self.orci.I[0]
        self.toRAM_DI = [self.brntr[i] for i in range(self.nbit)]
        self.Clk = [self.latchH.Clk, self.latchM.Clk, self.latchL.Clk]
        self.Enable = [self.triH.Enable, self.triM.Enable, self.triL.Enable]

        super().__init__(self.device_name, self.name)
    
    def set_input(self, A: int):
        if A < 0 or A > 2**self.nbit - 1:
            raise(RuntimeError)
        strA = i2b_ri(A, self.nbit)
        for i in range(self.nbit):
            self.A[i].value = strA[i]

    def get_output(self):
        return pav2i(self.brntr, self.nbit)


class TripleByteAccumulator(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'TripleByteAccumulator'
        self.name = name
        self.naddr = 4
        self.nbit = 8

        self.cs = ControlSignal('cs')
        self.counter = RippleCounter4Bit('counter')
        self.ram = RAM256x8('ram')
        self.adder = AccumulatingAdder('adder')
        self.sel = Selector2to1xN('sel', self.naddr)

        self.cs.ToCounterClk >> self.counter.Clk
        self.cs.ToLatchClk >> self.adder.Clk
        self.cs.ToRamW >> self.sel.wB
        self.sel.wO >> self.ram.W
        self.sel.eB.set()
        self.sel.eO >> self.ram.E
        for i in range(self.naddr):
            self.counter.Q[i] >> self.sel.addrB[i]
            self.sel.addrO[i] >> self.ram.A[i]
        for i in range(self.nbit):
            self.ram.DO[i] >> self.adder.DI[i] >> self.cs.DI[i]
            self.adder.DO[i] >> self.sel.diB[i]
            self.sel.diO[i] >> self.ram.DI[i]
        
        self.update_sequence = [self.cs, self.counter, self.ram, self.adder, self.sel, self.ram]

        self.sel.setB()

        super().__init__(self.device_name, self.name)
    
    def init(self):
        self.counter.init()

    def write_data(self, data):
        self.sel.setA()
        self.sel.wA.set()
        for addr, d in enumerate(data):
            self.sel.set_addrA(addr)
            self.sel.set_inputA(d)
            self.sel.step()
            self.ram.step()
        self.sel.wA.reset()
        self.sel.setB()
    
    def read_data(self, addr):
        # self.sel.setA()
        # self.sel.set_addrA(addr)
        # self.sel.wA.reset()
        # self.sel.eA.set()
        # self.sel.step()
        # self.ram.step()
        # data = self.ram.get_output()
        # self.sel.eA.reset()
        # self.sel.setB()
        strDO = ''.join([str(self.ram.cell[0].cell[addr][i].DO.value) for i in range(8)])[::-1]
        data = int(strDO, 2)
        return data
    

class TestAccumulator(unittest.TestCase):
    def test_control_signal(self):
        print('test_control_signal')

        cs = ControlSignal('cs')
        cs.power_on()

        for i in range(10):
            cs.step()
            # print(cs)
            if cs.ToLatchClk.value == 1:
                a=1

    def test_accumulating_adder(self):
        print('test_accumulating_adder')

        data = [
            [0xC8, 0xAF, 0x00],
            [0xB8, 0x88, 0x00],
        ]
        ndata = len(data)

        aa = AccumulatingAdder('aa')
        aa.power_on()

        sum = 0
        for i in range(ndata):
            sum += data[i][0] + data[i][1]*(2**8) + data[i][2]*(2**16)

            for k in range(3):
                aa.set_input(data[i][k])
                for j in range(3):
                    aa.Clk[j].reset()
                    aa.Enable[j].reset()
                aa.Clk[k].set()
                aa.Enable[k].set()
                aa.step()
            self.assertEqual(aa.get_output(), sum)

    def test_ram_write_read(self):
        print('test_ram_write_read')

        data = [
            0x01,
            0x02,
        ]
        ndata = len(data)

        aaa = AutomatedAccumulatingAdder('aaa')
        aaa.power_on()
        aaa.write_data(data)
        aaa.step()
        # print(aaa.ram)
        for i in range(ndata):
            self.assertEqual(aaa.read_data(i), data[i])

    def test_automated_accumulating_adder(self):
        print('test_automated_accumulating_adder')

        data = [
            0x35,
            0x1B,
            0x09,
            0x31,
            0x1E,
            0x12,
            0x23,
            0x0C,
        ]
        ndata = len(data)
        s = sum(data)

        aaa = AutomatedAccumulatingAdder('aaa')
        aaa.power_on()
        aaa.init()
        aaa.write_data(data)
        # print(aaa.ram)

        correct = False
        for i in range(40):
            aaa.step()
            res = aaa.read_data(ndata)
            if res != 0:
                self.assertEqual(res, s)
                correct = True
                break
            # print(' '.join([str(aaa.adder.brndi[i].value) for i in range(8)])[::-1])
            # print(' '.join([str(aaa.adder.brndo[i].value) for i in range(8)])[::-1])
            # print(aaa.cs)
            # print(aaa.counter)
        self.assertTrue(correct)
        print(aaa.ram.cell[0])


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        # TestAccumulator('test_control_signal'),
        TestAccumulator('test_accumulating_adder'),
        # TestAccumulator('test_ram_write_read'),
        # TestAccumulator('test_automated_accumulating_adder'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)