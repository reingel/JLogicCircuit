import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Util import *

class Ground:
    def __init__(self):
        self.vol = False

    def __repr__(self):
        return f"Ground({bool2int(self.vol)})"
    
    def vol(self):
        return self.vol


if __name__ == '__main__':
    grd = Ground()
    print(grd)