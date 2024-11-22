from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port


class Power(SimulatedCircuit):
    '''
    O: power output (HIGH or OPEN)
    '''
    def __init__(self, name):
        self.device_name = 'Power'
        self.name = name

        self.O = Port('O', self)

        super().__init__(self.device_name, self.name)

    def __repr__(self):
        return f"Power({self.name}, {self.O.value} -> )"

    def on(self):
        self.O.set()
    
    def off(self):
        self.O.reset()
    
    def update_inport(self):
        pass

    def update_state(self):
        pass
    
    def calc_output(self):
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




import unittest

class TestSource(unittest.TestCase):
    def test_power(self):
        print('test_power')

        pwr = Power('pwr1')
        pwr.step()
        self.assertEqual(pwr.O.value, OPEN)
        pwr.power_on()
        pwr.step()
        self.assertEqual(pwr.O.value, HIGH)
        pwr.off()
        pwr.step()
        self.assertEqual(pwr.O.value, OPEN)
    
    def test_ground(self):
        print('test_ground')

        grd = Ground('grd1')
        grd.step()
        self.assertEqual(grd.O.value, GND)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestSource('test_power'),
        TestSource('test_ground'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)