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

class Inverter(Device):
    def __init__(self, name):
        # create devices
        self.sw = Switch('sw')
        self.pwr = Power('pwr')
        self.rly = Relay('rly')

        # connect
        self.pwr.ri >> self.rly.up
        self.rly.ru >> self.sw.le
        self.sw.ri >> self.rly.le

        # ports
        self.out = self.rly.ru

        super().__init__(name)
    
    def __repr__(self):
        sw_volt = self.sw.state
        out_volt = self.get_output()
        return f'Interver({self.name}, sw = {bool2int(sw_volt)}, out = {bool2int(out_volt)})'

    def set_input(self, sw):
        self.sw.set_state(sw)
    
    def get_input(self):
        return self.sw.state
    
    def get_output(self):
        return self.rly.ru.volt
    
    def calc_output(self):
        self.sw.calc_output()
        self.rly.calc_output()
        
    def update(self):
        self.sw.update()
        self.rly.update()


class TestInverter(unittest.TestCase):
    def test_F(self):
        gate = Inverter('gate1')
        gate.set_input(LOW)
        gate.step()
        gate.step()
        gate.step()
        self.assertEqual(gate.get_output(), HIGH)
        print(gate)

    def test_T(self):
        gate = Inverter('gate2')
        gate.set_input(HIGH)
        print(bool2int(gate.rly.X), bool2int(gate.out.volt))
        for i in range(10):
            gate.step()
            print(bool2int(gate.rly.X), bool2int(gate.out.volt))

if __name__ == '__main__':
    unittest.main()