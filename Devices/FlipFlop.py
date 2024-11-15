import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Source import Power
from Relay import Relay
from Junction import Split, Split8
from Gate import And, Nor, Inverter

class RSFlipFlop(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'RSFlipFlop'

        # create elements
        self.nor1 = Nor('nor1')
        self.nor2 = Nor('nor2')
        self.spl1 = Split('spl1')
        self.spl2 = Split('spl2')

        # connect
        self.nor1.O >> self.spl1.I
        self.spl1.O1 >> self.nor2.I0
        self.nor2.O >> self.spl2.I
        self.spl2.O0 >> self.nor1.I1

        # create access ports
        self.R = self.nor1.I0
        self.S = self.nor2.I1
        self.Q = self.spl1.O0
        self.Qbar = self.spl2.O1

        # update sequences
        self.update_sequence = [self.nor2, self.spl2, self.nor1, self.spl1, self.nor2, self.spl2, self.nor1, self.spl1]

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
        self.spl1 = Split('spl1') # for Data
        self.spl2 = Split('spl2') # for Clock
        self.inv = Inverter('inv')
        self.and1 = And('and1')
        self.and2 = And('and2')
        self.rsff = RSFlipFlop('rsff')

        # connect
        self.spl1.O0 >> self.inv.I
        self.inv.O >> self.and1.I0
        self.spl1.O1 >> self.and2.I1
        self.spl2.O0 >> self.and1.I1
        self.spl2.O1 >> self.and2.I0
        self.and1.O >> self.rsff.R
        self.and2.O >> self.rsff.S

        # create access ports
        self.D = self.spl1.I
        self.Clk = self.spl2.I
        self.Q = self.rsff.Q
        self.Qbar = self.rsff.Qbar

        # update sequences
        self.update_sequence = [self.spl1, self.spl2, self.inv, self.and1, self.and2, self.rsff]

        super().__init__('LevelTriggeredDtypeFlipFlop', name)


class EdgeTriggeredDtypeFlipFlop(DtypeFlipFlop):
    def __init__(self, name):
        self.device_name = 'Edge-Triggered D-type FlipFlop'

        # create elements
        self.splc1 = Split('splc1') # for Clock 1
        self.splc2 = Split('splc2') # for Clock 2
        self.splc3 = Split('splc3') # for Clock 3
        self.spld1 = Split('spld1') # for Data
        self.inv1 = Inverter('inv1') # for Clock
        self.inv2 = Inverter('inv2') # for Data
        self.and1 = And('and1')
        self.and2 = And('and2')
        self.and3 = And('and3')
        self.and4 = And('and4')
        self.rsff1 = RSFlipFlop('rsff1')
        self.rsff2 = RSFlipFlop('rsff2')

        # connect
        self.splc1.O0 >> self.splc3.I
        self.splc1.O1 >> self.inv1.I
        self.inv1.O >> self.splc2.I
        self.splc2.O0 >> self.and1.I1
        self.splc2.O1 >> self.and2.I0
        self.spld1.O0 >> self.and1.I0
        self.spld1.O1 >> self.inv2.I
        self.inv2.O >> self.and2.I1
        self.and1.O >> self.rsff1.R
        self.and2.O >> self.rsff1.S
        self.rsff1.Q >> self.and3.I0
        self.rsff1.Qbar >> self.and4.I1
        self.splc3.O0 >> self.and3.I1
        self.splc3.O1 >> self.and4.I0
        self.and3.O >> self.rsff2.R
        self.and4.O >> self.rsff2.S

        # create access ports
        self.D = self.spld1.I
        self.Clk = self.splc1.I
        self.Q = self.rsff2.Q
        self.Qbar = self.rsff2.Qbar

        # update sequences
        self.update_sequence = [
            self.splc1, self.inv1, self.splc2, self.splc3,
            self.spld1, self.inv2,
            self.and1, self.and2, self.rsff1,
            self.and3, self.and4, self.rsff2,
            ]

        super().__init__('EdgeTriggeredDtypeFlipFlop', name)

class Latch8bit(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = '8-Bit Latch'

        self.nbit = 8
        self.split8 = Split8('split8')
        self.latches = []
        self.D = []
        self.Q = []

        self.update_sequence = [self.split8]

        for i in range(self.nbit):
            # create elements
            latch = EdgeTriggeredDtypeFlipFlop(f'latch{i:02d}')
            self.latches.append(latch)
            # connect
            self.split8.O[i] >> self.latches[i].Clk
            # create access ports
            self.D.append(self.latches[i].D)
            self.Q.append(self.latches[i].Q)
            # update sequences
            self.update_sequence.append(self.latches[i])
        
        self.Clk = self.split8.I

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
            [[0, 1], 0],
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
            [[0, 1], 1],
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
            dev.step()

            dev.Clk.set()
            dev.step()
            # print(dev.get_output())
            self.assertEqual(dev.get_output(), inp)

            dev.Clk.reset()
            dev.step()
            # print(dev.get_output())
            self.assertEqual(dev.get_output(), inp)



if __name__ == '__main__':
    unittest.main()