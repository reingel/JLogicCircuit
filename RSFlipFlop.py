import unittest
import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Constant import *
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
        ports = bool2int(np.array([self.R.volt, self.S.volt, self.Q.volt, self.Qbar.volt]))
        return f'RSFlipFlop({self.name}, [R S Q Qbar] = {ports}'

    def set_input(self, R, S):
        self.R.set_volt(R)
        self.S.set_volt(S)
    
    def get_output(self):
        return [self.Q.volt, self.Qbar.volt]
    
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
            print(f'{i+1:2}: ', bool2int(dev.R.volt), bool2int(dev.S.volt), bool2int(dev.Q.volt), bool2int(dev.Qbar.volt))
        print('')
        self.assertTrue(dev.Q.volt == HIGH and dev.Qbar.volt == LOW)

        dev.set_input(R=LOW, S=LOW)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.volt), bool2int(dev.S.volt), bool2int(dev.Q.volt), bool2int(dev.Qbar.volt))
        print('')
        self.assertTrue(dev.Q.volt == HIGH and dev.Qbar.volt == LOW)

    def test_reset(self):
        dev = RSFlipFlop('dev2')

        dev.set_input(R=HIGH, S=LOW)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.volt), bool2int(dev.S.volt), bool2int(dev.Q.volt), bool2int(dev.Qbar.volt))
        print('')
        self.assertTrue(dev.Q.volt == LOW and dev.Qbar.volt == HIGH)

        dev.set_input(R=LOW, S=LOW)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.volt), bool2int(dev.S.volt), bool2int(dev.Q.volt), bool2int(dev.Qbar.volt))
        print('')
        self.assertTrue(dev.Q.volt == LOW and dev.Qbar.volt == HIGH)

if __name__ == '__main__':
    unittest.main()