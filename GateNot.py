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

class GateNot(Device):
    def __init__(self, name):
        # U: input vector, X: state vector, Y: output vector
        self.nU = 1
        self.nY = 1

        self.pwr1 = Power('pwr1') # left of rly
        self.pwr2 = Power('pwr2') # up of rly
        self.sw = Switch('sw')
        self.rly = Relay('rly')

        self.pwr1.ri >> self.sw.le
        self.pwr2.ri >> self.rly.up
        self.sw.ri >> self.rly.le

        super().__init__(name)
    
    def __repr__(self):
        in_volt = self.sw.state
        out_volt = self.get_output()
        return f'GateNot({self.name}, in = {bool2int(in_volt)}, out = {bool2int(out_volt)})'

    def set_input(self, sw):
        self.sw.set_state(sw)
    
    def get_output(self):
        return self.rly.ru.volt
    
    def calc_output(self):
        self.sw.calc_output()
        self.rly.calc_output()
        
    def update(self):
        self.sw.update()
        self.rly.update()


class TestGateNot(unittest.TestCase):
    def test_F(self):
        gate = GateNot('gate1')
        gate.set_input(LOW)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), HIGH)
        print(gate)
        gate.update()

    def test_T(self):
        gate = GateNot('gate1')
        gate.set_input(HIGH)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), LOW)
        print(gate)
        gate.update()


if __name__ == '__main__':
    unittest.main()