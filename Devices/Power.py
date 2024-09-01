import numpy as np
import matplotlib.pyplot as plt
from BitValue import *
from Util import *
from Device import Device
from Source import Source
from Port import Port

class Power(Source):
    def __init__(self, name):
        self.ri = Port('ri', self, HIGH)
        super().__init__(name)

    def __repr__(self):
        return f"Power({self.name})"
    
    def calc_output(self):
        self.ri.set_value(HIGH)

    def update(self):
        pass

if __name__ == '__main__':
    pwr = Power('pwr1')
    print(pwr)
