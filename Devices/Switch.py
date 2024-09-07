import unittest
from EStatus import *
from Device import Device
from Port import Port
from Source import Power
from Relay import Relay

class Switch(Device):
    def __init__(self, name):
        self.state = OPEN # open

        self.le = Port('le', self)
        self.ri = Port('ri', self)

        # create access points
        self.in1 = self.le
        self.out = self.ri

        super().__init__('Switch', name)
    
    def __repr__(self):
        return f'Switch({self.le.status} -> [{self.state}] -> {self.ri.status})'
    
    def invert(self):
        if self.state == HIGH:
            self.state = OPEN
        elif self.state == OPEN:
            self.state = HIGH
        else:
            raise(RuntimeError)
    
    def set_state(self, state):
        self.state = state
    
    def calc_output(self):
        self.le.update_status()
        if self.state: # switch on
            self.ri.status = self.le.status
        else: # switch off
            self.ri.status = OPEN
    
    def update_state(self):
        pass # there is no state.

class TestSwitch(unittest.TestCase):
    def test_switch(self):
        sw = Switch('sw1')
        pwr = Power('pwr1')
        sw.le.connect(pwr.ri)
        sw.step()
        print(sw)
        sw.invert()
        sw.step()
        print(sw)
        sw.set_state(OPEN)
        sw.step()
        print(sw)

if __name__ == '__main__':
    unittest.main()