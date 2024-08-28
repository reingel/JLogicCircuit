import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Util import *
from Device import Device

class Source(Device):
    def __init__(self):
        self.vol = True

    def __repr__(self):
        return f"Source({bool2int(self.vol)})"
    
    def vol(self):
        return self.vol

if __name__ == '__main__':
    src = Source()
    print(src)
