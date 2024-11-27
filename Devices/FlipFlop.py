import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Branch import Branch
from Gate import And, Nor, Inverter

class RSFlipFlop(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'RSFlipFlop'

        # create elements
        self.nor1 = Nor('nor1')
        self.nor2 = Nor('nor2')
        self.brn1 = Branch('brn1')
        self.brn2 = Branch('brn2')

        # connect
        self.nor1.O >> self.brn1 >> self.nor2.I[0]
        self.nor2.O >> self.brn2 >> self.nor1.I[1]

        # create access ports
        self.R = self.nor1.I[0]
        self.S = self.nor2.I[1]
        self.Q = self.brn1
        self.Qbar = self.brn2

        # update sequences
        self.update_sequence = [self.nor2, self.brn2, self.nor1, self.brn1, self.nor2, self.brn2, self.nor1, self.brn1]

        super().__init__('RSFlipFlop', name)
    
    def __repr__(self):
        str = f'RSFlipFlop({self.name}, [S R Q Qbar] = [{self.S.value} {self.R.value} {self.Q.value} {self.Qbar.value}]'
        return str

    def get_output(self):
        return self.Q.value


class DtypeFlipFlop(SimulatedCircuit):
    def __init__(self, device_name, name):
        super().__init__(device_name, name)

    def __repr__(self):
        str = f'{self.device_name}({self.name}, [D Clk Q Qbar] = [{self.D.value} {self.Clk.value} {self.Q.value} {self.Qbar.value}]'
        return str

class LevelTriggeredDtypeFlipFlop(DtypeFlipFlop):
    def __init__(self, name):
        self.device_name = 'Level-Triggered D-type FlipFlop'

        # create elements
        self.brn1 = Branch('brn1') # for Data
        self.brn2 = Branch('brn2') # for Clock
        self.inv = Inverter('inv')
        self.and1 = And('and1')
        self.and2 = And('and2')
        self.rsff = RSFlipFlop('rsff')

        # connect
        self.brn1 >> self.inv.I
        self.inv.O >> self.and1.I[0]
        self.brn1 >> self.and2.I[1]
        self.brn2 >> (self.and1.I[1], self.and2.I[0])
        self.and1.O >> self.rsff.R
        self.and2.O >> self.rsff.S

        # create access ports
        self.D = self.brn1
        self.Clk = self.brn2
        self.Q = self.rsff.Q
        self.Qbar = self.rsff.Qbar

        # update sequences
        self.update_sequence = [self.brn1, self.brn2, self.inv, self.and1, self.and2, self.rsff]

        super().__init__('LevelTriggeredDtypeFlipFlop', name)


class EdgeTriggeredDtypeFlipFlop(DtypeFlipFlop):
    def __init__(self, name):
        self.device_name = 'Edge-Triggered D-type FlipFlop'

        # create elements
        self.brnc1 = Branch('brnc1') # for Clock 1
        self.brnc2 = Branch('brnc2') # for Clock 2
        self.brnc3 = Branch('brnc3') # for Clock 3
        self.brnd1 = Branch('brnd1') # for Data
        self.inv1 = Inverter('inv1') # for Clock
        self.inv2 = Inverter('inv2') # for Data
        self.and1 = And('and1')
        self.and2 = And('and2')
        self.and3 = And('and3')
        self.and4 = And('and4')
        self.rsff1 = RSFlipFlop('rsff1')
        self.rsff2 = RSFlipFlop('rsff2')

        # connect
        self.brnc1 >> (self.brnc3, self.inv1.I)
        self.inv1.O >> self.brnc2 >> (self.and1.I[1], self.and2.I[0])
        self.brnd1 >> (self.and1.I[0], self.inv2.I)
        self.inv2.O >> self.and2.I[1]
        self.and1.O >> self.rsff1.R
        self.and2.O >> self.rsff1.S
        self.rsff1.Q >> self.and3.I[0]
        self.rsff1.Qbar >> self.and4.I[1]
        self.brnc3 >> (self.and3.I[1], self.and4.I[0])
        self.and3.O >> self.rsff2.R
        self.and4.O >> self.rsff2.S

        # create access ports
        self.D = self.brnd1
        self.Clk = self.brnc1
        self.Q = self.rsff2.Q
        self.Qbar = self.rsff2.Qbar

        # update sequences
        self.update_sequence = [
            self.brnc1, self.inv1, self.brnc2, self.brnc3,
            self.brnd1, self.inv2,
            self.and1, self.and2, self.rsff1,
            self.and3, self.and4, self.rsff2,
            ]

        super().__init__('EdgeTriggeredDtypeFlipFlop', name)

class Latch8bit(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = '8-Bit Latch'

        self.nbit = 8

        self.Clk = Port('I', self)
        self.brn = Branch('brn')
        self.latch = [EdgeTriggeredDtypeFlipFlop(f'latch{i:02d}') for i in range(self.nbit)]
        # self.latch = [LevelTriggeredDtypeFlipFlop(f'latch{i:02d}') for i in range(self.nbit)]

        self.Clk >> self.brn
        for i in range(self.nbit):
            self.brn >> self.latch[i].Clk

        self.D = [self.latch[i].D for i in range(self.nbit)]
        self.Q = [self.latch[i].Q for i in range(self.nbit)]

        self.update_sequence = [self.brn]
        self.update_sequence.extend([self.latch[i] for i in range(self.nbit)])

        super().__init__('Latch8bit', name)
        
    def set_input(self, D: int):
        if D > 255 or D < 0:
            raise(RuntimeError)
        strD = f'{D:08b}'[::-1]
        for i in range(self.nbit):
            self.D[i].value = int(strD[i])
    
    def get_output(self):
        strQ = ''
        for i in range(self.nbit):
            strQ = f'{self.Q[i].value}{strQ}'
        Q = int(strQ, 2)
        return Q





class TestFlipFlop(unittest.TestCase):
    def test_rsff(self):
        print('test_rsff')

        dev = RSFlipFlop('rsff1')
        dev.power_on()
        dev.step()

        io = [ # [[S, R], Q],
            [[0, 0], 0],
            [[1, 0], 1],
            [[0, 0], 1],
            [[0, 1], 0],
            [[0, 0], 0],
        ]

        for i in range(len(io)):
            dev.S.value = io[i][0][0]
            dev.R.value = io[i][0][1]
            dev.step()
            self.assertTrue(dev.Q.value == io[i][1])
            self.assertNotEqual(dev.Q.value, dev.Qbar.value)

    def test_ltdff(self):
        print('test_ltdff')

        ff = LevelTriggeredDtypeFlipFlop('ltdff')
        ff.power_on()
        ff.step()

        io = [ # [[D, Clk], Q],
            [[0, 0], 0],
            [[1, 0], 0],
            [[1, 1], 1],
            [[0, 1], 0], # Q goes down because Level Triggered Type
            [[0, 0], 0],
            [[0, 1], 0],
            [[0, 0], 0],
        ]

        for i in range(len(io)):
            ff.D.value = io[i][0][0]
            ff.Clk.value = io[i][0][1]
            ff.step()
            self.assertTrue(ff.Q.value == io[i][1])
            self.assertNotEqual(ff.Q.value, ff.Qbar.value)

    def test_etdff(self):
        print('test_etdff')

        ff = EdgeTriggeredDtypeFlipFlop('etdff')
        ff.power_on()
        ff.step()

        io = [ # [[D, Clk], Q],
            [[0, 0], 0],
            [[1, 0], 0],
            [[1, 1], 1],
            [[0, 1], 1], # Q don't go down because Edge Triggered
            [[0, 0], 1],
            [[0, 1], 0],
            [[0, 0], 0],
        ]

        for i in range(len(io)):
            ff.D.value = io[i][0][0]
            ff.Clk.value = io[i][0][1]
            ff.step()
            self.assertTrue(ff.Q.value == io[i][1])
            self.assertNotEqual(ff.Q.value, ff.Qbar.value)

    def test_etdff_feedback(self):
        print('test_etdff_feedback')

        ff = EdgeTriggeredDtypeFlipFlop('etdff1')
        ff.Qbar >> ff.D

        ff.power_on()
        ff.step()

        Qbar1 = 1
        for i in range(5):
            ff.Clk.reset()
            ff.step()
            self.assertEqual(ff.D.value, Qbar1)

            ff.Clk.set()
            ff.step()
            self.assertEqual(ff.D.value, ff.Q.value)

            Qbar1 = ff.Qbar.value

    def test_latch8(self):
        print('test_latch8')

        dev = Latch8bit('latch8')
        dev.power_on()
        dev.Clk.reset()
        dev.step()
        # print(dev)

        for i in range(10):
            inp = i*3 + 1
            dev.set_input(inp)
            dev.step() # not needed if Level Triggered is used

            dev.Clk.set()
            dev.step()
            # print(dev.get_output())
            self.assertEqual(dev.get_output(), inp)

            dev.Clk.reset()
            dev.step()
            # print(dev.get_output())
            self.assertEqual(dev.get_output(), inp)



if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestFlipFlop('test_rsff'),
        TestFlipFlop('test_ltdff'),
        TestFlipFlop('test_etdff'),
        TestFlipFlop('test_etdff_feedback'),
        TestFlipFlop('test_latch8'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)