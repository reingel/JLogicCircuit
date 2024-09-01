import unittest
import numpy as np
import matplotlib.pyplot as plt
from BitValue import *
from Util import *
from Device import Device
from Power import Power
from Ground import Ground
from Relay import Relay
from Switch import Switch
from GateNor import GateNor

class RSFlipFlop(Device):
    def __init__(self, name):
        # create devices
        self.nor1 = GateNor('nor1', init_charges=[LOW, HIGH])
        self.nor2 = GateNor('nor2', init_charges=[LOW, LOW])

        # connect
        self.nor1.out >> self.nor2.in1
        self.nor2.out >> self.nor1.in2

        # create external ports
        self.R = self.nor1.in1
        self.S = self.nor2.in2
        self.Q = self.nor1.out
        self.Qbar = self.nor2.out

        super().__init__(name)
    
    def __repr__(self):
        ports = bool2int(np.array([self.R.value, self.S.value, self.Q.value, self.Qbar.value]))
        return f'RSFlipFlop({self.name}, [R S Q Qbar] = {ports}'

    def set_input(self, R, S):
        self.R.set_value(R)
        self.S.set_value(S)
    
    def get_output(self):
        return [self.Q.value, self.Qbar.value]
    
    def calc_output(self):
        # self.nor1.in1.update()
        # self.nor1.in2.update()
        # self.nor2.in1.update()
        # self.nor2.in2.update()
        self.nor1.calc_output()
        self.nor2.calc_output()
        
    def update(self):
        self.nor1.update()
        self.nor2.update()


class TestRSFlipFlop(unittest.TestCase):
    nRepeat = 5

    def test_set(self):
        dev = RSFlipFlop('dev1')

        dev.set_input(R=LOW, S=HIGH)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.value), bool2int(dev.S.value), bool2int(dev.Q.value), bool2int(dev.Qbar.value))
        print('')
        self.assertTrue(dev.Q.value == HIGH and dev.Qbar.value == LOW)

        dev.set_input(R=LOW, S=LOW)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.value), bool2int(dev.S.value), bool2int(dev.Q.value), bool2int(dev.Qbar.value))
        print('')
        self.assertTrue(dev.Q.value == HIGH and dev.Qbar.value == LOW)

    def test_reset(self):
        dev = RSFlipFlop('dev2')

        dev.set_input(R=HIGH, S=LOW)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.value), bool2int(dev.S.value), bool2int(dev.Q.value), bool2int(dev.Qbar.value))
        print('')
        self.assertTrue(dev.Q.value == LOW and dev.Qbar.value == HIGH)

        dev.set_input(R=LOW, S=LOW)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.value), bool2int(dev.S.value), bool2int(dev.Q.value), bool2int(dev.Qbar.value))
        print('')
        self.assertTrue(dev.Q.value == LOW and dev.Qbar.value == HIGH)

if __name__ == '__main__':
    unittest.main()