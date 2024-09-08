import unittest
from BitValue import *
from Device import Device
from Source import Power
from Relay import Relay
from Connection import Split
from Gate import And, Nor, Inverter

class RSFlipFlop(Device):
    def __init__(self, name):
        self.device_name = 'RSFlipFlop'

        # create devices
        self.nor1 = Nor('nor1')
        self.nor2 = Nor('nor2')
        self.spl1 = Split('spl1')
        self.spl2 = Split('spl2')

        # initialize
        self.nor1.rly1.X = OPEN
        self.nor1.rly2.X = HIGH
        self.nor2.rly1.X = OPEN
        self.nor2.rly2.X = OPEN
        self.nor1.in2.value = HIGH

        # connect
        self.nor1.out >> self.spl1.in1
        self.spl1.out2 >> self.nor2.in1
        self.nor2.out >> self.spl2.in1
        self.spl2.out1 >> self.nor1.in2

        # create external ports
        self.R = self.nor1.in1
        self.S = self.nor2.in2
        self.Q = self.spl1.out1
        self.Qbar = self.spl2.out2

        # update sequences
        self.inports = [self.R, self.S]
        self.update_sequence = [self.nor1, self.nor2, self.spl1, self.spl2, self.nor1]

        super().__init__('RSFlipFlop', name)
    
    def __repr__(self):
        str = f'RSFlipFlop({self.name}, [S R Q Qbar] = [{self.S.value} {self.R.value} {self.Q.value} {self.Qbar.value}]'
        # str += '\n'
        # for device in self.update_sequence:
        #     str += f'    {device}\n'
        return str

    def set_input(self, S, R):
        self.S.value = S
        self.R.value = R
    
    def get_output(self):
        return self.Q.value


class DtypeFlipFlop(Device):
    def __init__(self, device_name, name):
        super().__init__(device_name, name)

    def __repr__(self):
        str = f'{self.device_name}({self.name}, [D Clk Q Qbar] = [{self.D.value} {self.Clk.value} {self.Q.value} {self.Qbar.value}]'
        # str += '\n'
        # for device in self.update_sequence:
        #     str += f'  {device}\n'
        return str

class LevelTriggeredDtypeFlipFlip(DtypeFlipFlop):
    def __init__(self, name):
        self.device_name = 'Level-Triggered D-type FlipFlop'

        # create devices
        self.spl1 = Split('spl1') # for Data
        self.spl2 = Split('spl2') # for Clock
        self.inv = Inverter('inv')
        self.and1 = And('and1')
        self.and2 = And('and2')
        self.rsff = RSFlipFlop('rsff')

        # connect
        self.spl1.out1 >> self.inv.in1
        self.inv.out >> self.and1.in1
        self.spl1.out2 >> self.and2.in2
        self.spl2.out1 >> self.and1.in2
        self.spl2.out2 >> self.and2.in1
        self.and1.out >> self.rsff.R
        self.and2.out >> self.rsff.S

        # create external ports
        self.D = self.spl1.in1
        self.Clk = self.spl2.in1
        self.Q = self.rsff.Q
        self.Qbar = self.rsff.Qbar

        # update sequences
        self.inports = [self.D, self.Clk]
        self.update_sequence = [self.spl1, self.spl2, self.inv, self.and1, self.and2, self.rsff]

        super().__init__('LevelTriggeredDtypeFlipFlip', name)


class EdgeTriggeredDtypeFlipFlip(DtypeFlipFlop):
    def __init__(self, name):
        self.device_name = 'Edge-Triggered D-type FlipFlop'

        # create devices
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
        self.splc1.out1 >> self.splc3.in1
        self.splc1.out2 >> self.inv1.in1
        self.inv1.out >> self.splc2.in1
        self.splc2.out1 >> self.and1.in2
        self.splc2.out2 >> self.and2.in1
        self.spld1.out1 >> self.and1.in1
        self.spld1.out2 >> self.inv2.in1
        self.inv2.out >> self.and2.in2
        self.and1.out >> self.rsff1.R
        self.and2.out >> self.rsff1.S
        self.rsff1.Q >> self.and3.in1
        self.rsff1.Qbar >> self.and4.in2
        self.splc3.out1 >> self.and3.in2
        self.splc3.out2 >> self.and4.in1
        self.and3.out >> self.rsff2.R
        self.and4.out >> self.rsff2.S

        # create external ports
        self.D = self.spld1.in1
        self.Clk = self.splc1.in1
        self.Q = self.rsff2.Q
        self.Qbar = self.rsff2.Qbar

        # update sequences
        self.inports = [self.D, self.Clk]
        self.update_sequence = [
            self.splc1, self.inv1, self.splc2, self.splc3,
            self.spld1, self.inv2,
            self.and1, self.and2, self.rsff1,
            self.and3, self.and4, self.rsff2,
            ]

        super().__init__('EdgeTriggeredDtypeFlipFlip', name)


class TestFlipFlop(unittest.TestCase):
    def test_rsff(self):
        dev = RSFlipFlop('rsff1')

        dev.set_input(S=HIGH, R=OPEN)
        dev.step(n=4)
        print(dev)
        self.assertTrue(dev.Q.value == HIGH and dev.Qbar.value == OPEN)

        dev.set_input(S=OPEN, R=OPEN)
        dev.step(n=4)
        print(dev)
        self.assertTrue(dev.Q.value == HIGH and dev.Qbar.value == OPEN)

        dev.set_input(S=OPEN, R=HIGH)
        dev.step(n=4)
        print(dev)
        self.assertTrue(dev.Q.value == OPEN and dev.Qbar.value == HIGH)

        dev.set_input(S=OPEN, R=OPEN)
        dev.step(n=4)
        print(dev)
        self.assertTrue(dev.Q.value == OPEN and dev.Qbar.value == HIGH)


    def test_ltdff(self):
        ff = LevelTriggeredDtypeFlipFlip('ltdff')

        ff.D.value = OPEN
        ff.Clk.value = OPEN
        ff.step(n=2)
        print(ff)
        self.assertTrue(ff.Q.value == OPEN and ff.Qbar.value == HIGH)

        ff.D.value = HIGH
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == OPEN and ff.Qbar.value == HIGH)

        ff.Clk.value = HIGH
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == HIGH and ff.Qbar.value == OPEN)

        ff.Clk.value = OPEN
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == HIGH and ff.Qbar.value == OPEN)

        ff.D.value = OPEN
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == HIGH and ff.Qbar.value == OPEN)


    def test_etdff(self):
        ff = EdgeTriggeredDtypeFlipFlip('etdff')

        ff.D.value = OPEN
        ff.Clk.value = OPEN
        ff.step(n=2)
        print(ff)
        self.assertTrue(ff.Q.value == OPEN and ff.Qbar.value == HIGH)

        ff.D.value = HIGH
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == OPEN and ff.Qbar.value == HIGH)

        ff.Clk.value = HIGH
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == HIGH and ff.Qbar.value == OPEN)

        ff.D.value = OPEN
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == HIGH and ff.Qbar.value == OPEN)



if __name__ == '__main__':
    unittest.main()