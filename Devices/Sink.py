import numpy as np
import matplotlib.pyplot as plt
from EStatus import *
from Util import *
from Device import Device
from Port import Port


class Sink(Device):
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f"Sink({self.name})"
    
    def calc_output(self):
        pass

    def update_state(self):
        pass

if __name__ == '__main__':
    snk = Sink('snk1')
    print(snk)
