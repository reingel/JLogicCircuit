import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Source import Source
from Ground import Ground

class SimLogicGate:
    def __init__(self, dt=0.05*s):
        pass

    def __repr__(self):
        return f'SimLogicGate()'
    
    def step(self):
        pass
    
    def output(self):
        pass
    
    def update(self):
        pass


if __name__ == '__main__':
    sim = SimLogicGate()
    print(sim)