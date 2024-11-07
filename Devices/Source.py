import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port


class Power(SimulatedCircuit):
    def __init__(self, name):
        self.ri = Port('ri', self)

        self.state = OPEN

        self.out = self.ri

        super().__init__('Power', name)

    def __repr__(self):
        return f"Power({self.name}, {self.out.value} -> )"

    def on(self):
        self.state = HIGH
    
    def off(self):
        self.state = OPEN
    
    def update_inport(self):
        pass
    
    def calc_output(self):
        self.ri.value = self.state

    def update_state(self):
        pass


class Ground(SimulatedCircuit):
    def __init__(self, name):
        self.ri = Port('le', self)

        self.O = self.ri

        super().__init__('Ground', name)

    def __repr__(self):
        return f"Ground({self.name}, {self.O.value} -> )"
    
    def update_inport(self):
        pass
    
    def calc_output(self):
        self.ri.value = GND

    def update_state(self):
        pass



class TestSource(unittest.TestCase):
    def test_power(self):
        pwr = Power('pwr1')
        pwr.step()
        print(pwr)
        pwr.power_on()
        pwr.step()
        print(pwr)
        pwr.off()
        pwr.step()
        print(pwr)
    
    def test_ground(self):
        grd = Ground('grd1')
        grd.step()
        print(grd)


if __name__ == '__main__':
    unittest.main()