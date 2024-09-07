import unittest
from EStatus import *
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
        self.nor1.in1.status = HIGH
        self.nor2.in2.status = OPEN
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
        return f'RSFlipFlop({self.name}, [S R Q Qbar] = [{self.S.status} {self.R.status} {self.Q.status} {self.Qbar.status}]'

    def set_input(self, S, R):
        self.S.status = S
        self.R.status = R
    
    def get_output(self):
        return self.Q.status


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
        return f'LevelTriggeredDtypeFlipFlip({self.name}, [D Clk Q Qbar] = [{self.D.status} {self.Clk.status} {self.Q.status} {self.Qbar.status}]'


class TestRSFlipFlop(unittest.TestCase):
    nRepeat = 4

    def test_set(self):
        dev = RSFlipFlop('dev1')
        print('init', dev)

        dev.set_input(S=HIGH, R=OPEN)
        dev.step(n=self.nRepeat)
        print(dev)
        self.assertTrue(dev.Q.status == HIGH and dev.Qbar.status == OPEN)

        dev.set_input(S=OPEN, R=OPEN)
        dev.step(n=self.nRepeat)
        print(dev)
        self.assertTrue(dev.Q.status == HIGH and dev.Qbar.status == OPEN)

    def test_reset(self):
        dev = RSFlipFlop('dev2')
        print('init', dev)


        dev.set_input(S=OPEN, R=HIGH)
        dev.step(n=self.nRepeat)
        print(dev)
        self.assertTrue(dev.Q.status == OPEN and dev.Qbar.status == HIGH)

        dev.set_input(S=OPEN, R=OPEN)
        dev.step(n=self.nRepeat)
        print(dev)
        self.assertTrue(dev.Q.status == OPEN and dev.Qbar.status == HIGH)

class TestLevelTriggeredDtypeFlipFlop(unittest.TestCase):
    def test_ltdff(self):
        ff = LevelTriggeredDtypeFlipFlip('ltdff')

        ff.D.status = OPEN
        ff.Clk.status = HIGH
        ff.step(n=4)
        print(ff)
        self.assertTrue(ff.Q.status == OPEN and ff.Qbar.status == HIGH)

        ff.D.status = HIGH
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.status == HIGH and ff.Qbar.status == OPEN)

        ff.D.status = OPEN
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.status == OPEN and ff.Qbar.status == HIGH)

        ff.Clk.status = OPEN
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.status == OPEN and ff.Qbar.status == HIGH)

        ff.D.status = HIGH
        ff.step(n=6)
        print(ff)
        self.assertTrue(ff.Q.status == OPEN and ff.Qbar.status == HIGH)


if __name__ == '__main__':
    unittest.main()