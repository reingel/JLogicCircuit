import unittest
from BitValue import *
from Device import Device
from Port import Port
from Gate import Inverter

class Oscillator(Device):
    def __init__(self, name):
        self.inv = Inverter('inv')
        self.devices = [self.inv]

        self.inv.out >> self.inv.in1

        self.out = self.inv.out

        super().__init__('Oscillator', name)
    
    def __repr__(self):
        return f'Oscillator({self.name}, {self.out.value} -> )'
    

class TestClock(unittest.TestCase):
    def test_oscillator(self):
        osc = Oscillator('osc1')
        print(osc)
        osc.step(n=2)
        print(osc)
        osc.step(n=2)
        print(osc)
        osc.step(n=2)
        print(osc)
        osc.step(n=2)
        print(osc)



if __name__ == '__main__':
    unittest.main()