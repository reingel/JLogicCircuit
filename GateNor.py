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

class GateNor(Device):
    def __init__(self, name):
        # U: input vector, X: state vector, Y: output vector
        self.nU = 2
        self.nY = 1

        # creat devices
        self.pwr = Power('pwr') # up of rly1
        self.rly1 = Relay('rly1')
        self.rly2 = Relay('rly2')

        # connect
        self.pwr.ri.connect(self.rly1.up)
        self.rly1.ru.connect(self.rly2.up)

        # make ports using aliases
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.rly2.ru

        super().__init__(name)

    def __repr__(self):
        return f'GateNor({self.name}, in = {bool2int(self.get_input())}, out = {bool2int(self.get_output())})'

    def set_input(self, v1: bool, v2: bool):
        # self.rly1.le.set_volt(v1)
        # self.rly2.le.set_volt(v2)
        self.in1.set_volt(v1)
        self.in2.set_volt(v2)

    def get_input(self):
        return np.array([self.rly1.le.volt, self.rly2.le.volt])
    
    def get_output(self):
        return self.rly2.ru.volt
    
    def calc_output(self):
        self.rly1.calc_output()
        self.rly2.calc_output()
        
    def update(self):
        self.rly1.update()
        self.rly2.update()


class TestGateNor(unittest.TestCase):
    def test_FF(self):
        gate = GateNor('gate1')
        gate.set_input(LOW, LOW)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), HIGH)
        print(gate)
        gate.update()

    def test_TF(self):
        gate = GateNor('gate2')
        gate.set_input(HIGH, LOW)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), LOW)
        print(gate)
        gate.update()

    def test_FT(self):
        gate = GateNor('gate3')
        gate.set_input(LOW, HIGH)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), LOW)
        print(gate)
        gate.update()

    def test_TT(self):
        gate = GateNor('gate4')
        gate.set_input(HIGH, HIGH)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), LOW)
        print(gate)
        gate.update()



if __name__ == '__main__':
    unittest.main()