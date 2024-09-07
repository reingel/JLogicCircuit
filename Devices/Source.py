import unittest
from EStatus import *
from Device import Device
from Port import Port


class Power(Device):
    def __init__(self, name):
        self.ri = Port('ri', self, HIGH)

        self.out = self.ri

        super().__init__('Power', name)

    def __repr__(self):
        return f"Power({self.name}, {self.out.status} -> )"
    
    def calc_output(self):
        self.ri.status = HIGH

    def update_state(self):
        pass


class TestPower(unittest.TestCase):
    def test_power(self):
        pwr = Power('pwr1')
        print(pwr)


if __name__ == '__main__':
    unittest.main()