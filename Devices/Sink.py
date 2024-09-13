import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port


class Ground(SimulatedCircuit):
    def __init__(self, name):
        self.le = Port('le', self)

        self.in1 = self.le

        super().__init__('Ground', name)

    def __repr__(self):
        return f"Ground({self.name}, -> {self.in1.value})"
    
    def update_inport(self):
        pass
    
    def calc_output(self):
        self.le.value = OPEN

    def update_state(self):
        pass

if __name__ == '__main__':
    grd = Ground('grd1')
    print(grd)
