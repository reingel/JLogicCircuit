import numpy as np
import matplotlib.pyplot as plt
from EStatus import *
from Util import *
from Device import Device
from Sink import Sink
from Port import Port


class Terminator(Sink):
    def __init__(self, name):
        self.le = Port('le', self, OPEN)
        super().__init__(name)

    def __repr__(self):
        return f"Terminator({self.name})"
    
    def calc_output(self):
        pass

    def update(self):
        pass

if __name__ == '__main__':
    term = Terminator('term1')
    print(term)
