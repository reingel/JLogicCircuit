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
        self.devices = [self.nor1, self.nor2]

        # initialize
        self.nor1.in1.value = HIGH
        self.nor2.in2.value = OPEN
        self.step(n=4)

        # connect
        self.nor1.out >> self.nor2.in1
        self.nor2.out >> self.nor1.in2

        # create external ports
        self.R = self.nor1.in1
        self.S = self.nor2.in2
        self.Q = self.nor1.out
        self.Qbar = self.nor2.out

        super().__init__('RSFlipFlop', name)
    
    def __repr__(self):
        return f'RSFlipFlop({self.name}, [S R Q Qbar] = [{self.S.value} {self.R.value} {self.Q.value} {self.Qbar.value}]'

    def set_input(self, S, R):
        self.S.value = S
        self.R.value = R
    
    def get_output(self):
        return self.Q.value


class LevelTriggeredDtypeFlipFlip(Device):
    def __init__(self, name):
        self.device_name = 'Level-Triggered D-type FlipFlop'

        # create devices
        self.spl1 = Split('spl1') # for Data
        self.spl2 = Split('spl2') # for Clock
        self.inv = Inverter('inv')
        self.and1 = And('and1')
        self.and2 = And('and2')
        self.rsff = RSFlipFlop('rsff')
        self.devices = [self.spl1, self.spl2, self.inv, self.and1, self.and2, self.rsff]

        # connect
        self.spl1.ru >> self.inv.in1
        self.inv.out >> self.and1.in1
        self.spl1.rd >> self.and2.in2
        self.spl2.ru >> self.and1.in2
        self.spl2.rd >> self.and2.in1
        self.and1.out >> self.rsff.R
        self.and2.out >> self.rsff.S

        # create external ports
        self.D = self.spl1.le
        self.Clk = self.spl2.le
        self.Q = self.rsff.Q
        self.Qbar = self.rsff.Qbar

        super().__init__('LevelTriggeredDtypeFlipFlip', name)
    
    def __repr__(self):
        return f'LevelTriggeredDtypeFlipFlip({self.name}, [D Clk Q Qbar] = [{self.D.value} {self.Clk.value} {self.Q.value} {self.Qbar.value}]'


class TestRSFlipFlop(unittest.TestCase):
    nRepeat = 4

    def test_set(self):
        dev = RSFlipFlop('dev1')
        print('init', dev)

        dev.set_input(S=HIGH, R=OPEN)
        dev.step(n=self.nRepeat)
        print(dev)
        self.assertTrue(dev.Q.value == HIGH and dev.Qbar.value == OPEN)

        dev.set_input(S=OPEN, R=OPEN)
        dev.step(n=self.nRepeat)
        print(dev)
        self.assertTrue(dev.Q.value == HIGH and dev.Qbar.value == OPEN)

    def test_reset(self):
        dev = RSFlipFlop('dev2')
        print('init', dev)


        dev.set_input(S=OPEN, R=HIGH)
        dev.step(n=self.nRepeat)
        print(dev)
        self.assertTrue(dev.Q.value == OPEN and dev.Qbar.value == HIGH)

        dev.set_input(S=OPEN, R=OPEN)
        dev.step(n=self.nRepeat)
        print(dev)
        self.assertTrue(dev.Q.value == OPEN and dev.Qbar.value == HIGH)

class TestLevelTriggeredDtypeFlipFlop(unittest.TestCase):
    def test_ltdff(self):
        ff = LevelTriggeredDtypeFlipFlip('ltdff')

        ff.D.value = OPEN
        ff.Clk.value = HIGH
        ff.step(n=4)
        print(ff)
        self.assertTrue(ff.Q.value == OPEN and ff.Qbar.value == HIGH)

        ff.D.value = HIGH
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == HIGH and ff.Qbar.value == OPEN)

        ff.D.value = OPEN
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == OPEN and ff.Qbar.value == HIGH)

        ff.Clk.value = OPEN
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == OPEN and ff.Qbar.value == HIGH)

        ff.D.value = HIGH
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.value == OPEN and ff.Qbar.value == HIGH)


if __name__ == '__main__':
    unittest.main()