import numpy as np
import matplotlib.pyplot as plt
from EStatus import *
from Util import *
from Device import Device
from Sink import Sink
from Port import Port


class Ground(Sink):
    def __init__(self, name):
        self.le = Port('le', self, OPEN)
        super().__init__(name)

    def __repr__(self):
        return f"Ground({self.name})"
    
    def calc_output(self):
        pass

    def update(self):
        self.le.status = OPEN

if __name__ == '__main__':
    grd = Ground('grd1')
    print(grd)
