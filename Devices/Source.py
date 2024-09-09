import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port


class Power(SimulatedCircuit):
    def __init__(self, name):
        self.ri = Port('ri', self, HIGH)

        self.out = self.ri

        super().__init__('Power', name)

    def __repr__(self):
        return f"Power({self.name}, {self.out.value} -> )"
    
    def update_inport(self):
        pass
    
    def calc_output(self):
        self.ri.value = HIGH

    def update_state(self):
        pass



class TestSource(unittest.TestCase):
    def test_power(self):
        pwr = Power('pwr1')
        print(pwr)

if __name__ == '__main__':
    unittest.main()