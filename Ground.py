import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Util import *
from Device import Device
from Port import Port


class Ground(Device):
    def __init__(self):
        self.le = Port(False)

    def __repr__(self):
        return f"Ground({bool2int(self.le.volt)})"
    
    def vol(self):
        return self.le

if __name__ == '__main__':
    grd = Ground()
    print(grd)
