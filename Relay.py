import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Constant import *
from Util import *
from Source import Source
from Ground import Ground

class Relay:
    def __init__(self, source=Source(), ground=Ground()):
        self.source = source
        self.ground = ground

        # U: input vector, X: state vector, Y: output vector
        self.nU = 3
        self.nX = 1
        self.nY = 2

        # 0: switch in, 1: coil high, 2: coil low
        self.U = np.array([False] * self.nU)
        # actual coil voltage(considering delay), 0: current, 1: next
        self.X = np.array([False] * self.nX * 2)
        # 0: switch out up, 1: switch out down
        self.Y = np.array([False] * self.nY)

    def __repr__(self):
        return f'Relay(U = {bool2int(self.U)}, X = {bool2int(self.X)}, Y = {bool2int(self.Y)})'
    
    def set_switch_in_vol(self, vol: bool):
        self.U[0] = vol
    
    def set_coil_high_vol(self, vol: bool):
        self.U[1] = vol
    
    def output(self):
        self.X[1] = self.U[1] # next coil voltage = current coil high voltage
        if self.X[0] == True and self.U[2] == False: # coil is charged
            self.Y[0] = False
            self.Y[1] = self.U[0]
        elif self.X[0] == self.U[2]: # coil is discharged
            self.Y[0] = self.U[0]
            self.Y[1] = False
        
    def update(self):
        self.X[0] = self.X[1]


if __name__ == '__main__':
    rly = Relay()
    print(rly)

    rly.set_switch_in_vol(5*V)

    rly.set_coil_high_vol(5*V)
    rly.output()
    print(rly)
    rly.update()
    rly.output()
    print(rly)
    rly.update()

    rly.set_coil_high_vol(0*V)
    rly.output()
    print(rly)
    rly.update()
    rly.output()
    print(rly)
    rly.update()