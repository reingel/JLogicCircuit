import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Util import *
from Device import Device
from Port import Port

class Source(Device):
    def __init__(self):
        self.ri = Port(True)

    def __repr__(self):
        return f"Source({bool2int(self.ri.volt)})"
    
    def vol(self):
        return self.ri

if __name__ == '__main__':
    src = Source()
    print(src)
