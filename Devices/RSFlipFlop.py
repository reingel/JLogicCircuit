import unittest
import numpy as np
import matplotlib.pyplot as plt
from EStatus import *
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
        self.nor1 = GateNor('nor1', init_charges=[OPEN, HIGH])
        self.nor2 = GateNor('nor2', init_charges=[OPEN, OPEN])

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
        ports = bool2int(np.array([self.R.status, self.S.status, self.Q.status, self.Qbar.status]))
        return f'RSFlipFlop({self.name}, [R S Q Qbar] = {ports}'

    def set_input(self, R, S):
        self.R.status = R
        self.S.status = S
    
    def get_output(self):
        return [self.Q.status, self.Qbar.status]
    
    def calc_output(self):
        # self.nor1.in1.update_state()
        # self.nor1.in2.update_state()
        # self.nor2.in1.update_state()
        # self.nor2.in2.update_state()
        self.nor1.calc_output()
        self.nor2.calc_output()
        
    def update_state(self):
        self.nor1.update_state()
        self.nor2.update_state()


class TestRSFlipFlop(unittest.TestCase):
    nRepeat = 5

    def test_set(self):
        dev = RSFlipFlop('dev1')

        dev.set_input(R=OPEN, S=HIGH)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.status), bool2int(dev.S.status), bool2int(dev.Q.status), bool2int(dev.Qbar.status))
        print('')
        self.assertTrue(dev.Q.status == HIGH and dev.Qbar.status == OPEN)

        dev.set_input(R=OPEN, S=OPEN)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.status), bool2int(dev.S.status), bool2int(dev.Q.status), bool2int(dev.Qbar.status))
        print('')
        self.assertTrue(dev.Q.status == HIGH and dev.Qbar.status == OPEN)

    def test_reset(self):
        dev = RSFlipFlop('dev2')

        dev.set_input(R=HIGH, S=OPEN)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.status), bool2int(dev.S.status), bool2int(dev.Q.status), bool2int(dev.Qbar.status))
        print('')
        self.assertTrue(dev.Q.status == OPEN and dev.Qbar.status == HIGH)

        dev.set_input(R=OPEN, S=OPEN)
        for i in range(self.nRepeat):
            dev.step()
            print(f'{i+1:2}: ', bool2int(dev.R.status), bool2int(dev.S.status), bool2int(dev.Q.status), bool2int(dev.Qbar.status))
        print('')
        self.assertTrue(dev.Q.status == OPEN and dev.Qbar.status == HIGH)

if __name__ == '__main__':
    unittest.main()