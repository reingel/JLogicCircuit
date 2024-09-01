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

class GateNand(Device):
    def __init__(self, name):
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
        # self.rly1.ru >> self.rly2.ru

        super().__init__(name)
    
    def __repr__(self):
        in_volts = np.array([self.sw1.state, self.sw2.state])
        out_volt = self.get_output()
        return f'GateNand({self.name}, in = {bool2int(in_volts)}, out = {bool2int(out_volt)})'

    def set_input(self, sw1, sw2):
        self.sw1.set_state(sw1)
        self.sw2.set_state(sw2)
    
    def get_output(self):
        return self.rly1.ru.volt or self.rly2.ru.volt
    
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


class TestGateNand(unittest.TestCase):
    def test_FF(self):
        gate = GateNand('gate1')
        gate.set_input(LOW, LOW)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), HIGH)
        print(gate)
        gate.update()

    def test_TF(self):
        gate = GateNand('gate2')
        gate.set_input(HIGH, LOW)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), HIGH)
        print(gate)
        gate.update()

    def test_FT(self):
        gate = GateNand('gate3')
        gate.set_input(LOW, HIGH)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), HIGH)
        print(gate)
        gate.update()

    def test_TT(self):
        gate = GateNand('gate4')
        gate.set_input(HIGH, HIGH)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), LOW)
        print(gate)
        gate.update()



if __name__ == '__main__':
    unittest.main()