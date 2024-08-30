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

class GateOr(Device):
    def __init__(self, name):
        # U: input vector, X: state vector, Y: output vector
        self.nU = 2
        self.nY = 1

        self.pwr1 = Power('pwr1') # left of rly1
        self.pwr2 = Power('pwr2') # left of rly2
        self.pwr3 = Power('pwr3') # up of rly1
        self.pwr4 = Power('pwr4') # up of rly2
        self.sw1 = Switch('sw1')
        self.sw2 = Switch('sw2')
        self.rly1 = Relay('rly1')
        self.rly2 = Relay('rly2')

        self.pwr1.ri >> self.sw1.le
        self.pwr2.ri >> self.sw2.le
        self.pwr3.ri >> self.rly1.up
        self.pwr4.ri >> self.rly2.up
        self.sw1.ri >> self.rly1.le
        self.sw2.ri >> self.rly2.le
        # self.rly1.rd >> self.rly2.rd

        super().__init__(name)

    def __repr__(self):
        in_volts = np.array([self.sw1.state, self.sw2.state])
        out_volt = self.get_output()
        return f'GateOr({self.name}, in = {bool2int(in_volts)}, out = {bool2int(out_volt)})'

    def set_input(self, sw1, sw2):
        self.sw1.set_state(sw1)
        self.sw2.set_state(sw2)
    
    def get_output(self):
        return self.rly1.rd.volt or self.rly2.rd.volt
    
    def calc_output(self):
        self.sw1.calc_output()
        self.sw2.calc_output()
        self.rly1.calc_output()
        self.rly2.calc_output()
        
    def update(self):
        self.sw1.update()
        self.sw2.update()
        self.rly1.update()
        self.rly2.update()


class TestGateOr(unittest.TestCase):
    def test_FF(self):
        og = GateOr('og1')
        og.set_input(LOW, LOW)
        og.calc_output()
        og.update()
        og.calc_output()
        self.assertEqual(og.get_output(), LOW)
        print(og)
        og.update()

    def test_TF(self):
        og = GateOr('og2')
        og.set_input(HIGH, LOW)
        og.calc_output()
        og.update()
        og.calc_output()
        self.assertEqual(og.get_output(), HIGH)
        print(og)
        og.update()

    def test_FT(self):
        og = GateOr('og3')
        og.set_input(LOW, HIGH)
        og.calc_output()
        og.update()
        og.calc_output()
        self.assertEqual(og.get_output(), HIGH)
        print(og)
        og.update()

    def test_TT(self):
        og = GateOr('og4')
        og.set_input(HIGH, HIGH)
        og.calc_output()
        og.update()
        og.calc_output()
        self.assertEqual(og.get_output(), HIGH)
        print(og)
        og.update()



if __name__ == '__main__':
    unittest.main()