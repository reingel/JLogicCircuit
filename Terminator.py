import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Util import *
from Device import Device
from Port import Port


class Terminator(Device):
    def __init__(self, name):
        self.le = Port('grd.le', self, False)
        super().__init__(name)

    def __repr__(self):
        return f"Terminator({self.name})"
    
    def vol(self):
        return self.le

if __name__ == '__main__':
    term = Terminator('term1')
    print(term)
