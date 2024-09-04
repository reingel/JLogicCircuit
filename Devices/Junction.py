import unittest
import numpy as np
import matplotlib.pyplot as plt
from EStatus import *
from Util import *
from Device import Device
from Port import Port


class Junction(Device):
    def __init__(self, name):
        self.lu = Port('lu', self)
        self.ld = Port('ld', self)
        self.ri = Port('ri', self)

        super().__init__(name)
    
    def __repr__(self):
        return f'Junction(lu = {self.lu.status}, ld = {self.ld.status}, ri = {self.ri.status})'
    
    def calc_output(self):
        self.lu.update()
        self.ld.update()
        if self.lu.status == OPEN and self.ld.status == OPEN:
            self.ri.status = OPEN
        elif (self.lu.status == HIGH and self.ld.status == OPEN) or \
            (self.lu.status == OPEN and self.ld.status == HIGH) or \
            (self.lu.status == HIGH and self.ld.status == HIGH):
            self.ri.status = HIGH
        else:
            raise(RuntimeError)
    
    def update(self):
        pass # there is no state.

if __name__ == '__main__':
    jnc = Junction('jnc1')
    print(jnc)
    jnc.lu.status = HIGH
    jnc.calc_output()
    print(jnc)

