import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Source import Power
from Relay import Relay

class Switch(SimulatedCircuit):
    def __init__(self, name):
        self.state = OPEN # open

        self.le = Port('le', self)
        self.ri = Port('ri', self)

        # create access points
        self.I = self.le
        self.O = self.ri

        super().__init__('Switch', name)
    
    def __repr__(self):
        return f'Switch({self.le.value} -> [{self.state}] -> {self.ri.value})'
    
    def invert(self):
        if self.state == HIGH:
            self.state = OPEN
        elif self.state == OPEN:
            self.state = HIGH
        else:
            raise(RuntimeError)
    
    def set_state(self, state):
        self.state = state
    
    def update_inport(self):
        self.le.update_value()
    
    def calc_output(self):
        if self.state: # switch on
            self.ri.value = self.le.value
        else: # switch off
            self.ri.reset()
    
    def update_state(self):
        pass # there is no state.

class TestSwitch(unittest.TestCase):
    def test_switch(self):
        print('test_switch')

        sw = Switch('sw1')
        pwr = Power('pwr1')
        pwr.O >> sw.le
        pwr.on()
        pwr.step()

        sw.step()
        self.assertEqual(sw.state, OPEN)
        self.assertEqual(sw.O.value, OPEN)
        sw.invert()
        sw.step()
        self.assertEqual(sw.state, HIGH)
        self.assertEqual(sw.O.value, sw.I.value)
        sw.set_state(OPEN)
        sw.step()
        self.assertEqual(sw.state, OPEN)
        self.assertEqual(sw.O.value, OPEN)

if __name__ == '__main__':
    unittest.main()