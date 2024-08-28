import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Constant import *
from Util import *
from Device import Device
from Source import Source
from Ground import Ground
from Relay import Relay

class AndGate(Device):
    def __init__(self, source=Source(), ground=Ground()):
        self.source = source
        self.ground = ground

        # U: input vector, X: state vector, Y: output vector
        self.nU = 3
        self.nY = 1

        self.relay1 = Relay()
        self.relay2 = Relay()

        # 0: switch in, 1: coil high
        self.U = np.array([False] * self.nU)
        # 0: switch out up, 1: switch out down
        self.Y = np.array([False] * self.nY)
        # 0: actual coil voltage(considering delay)
        self.X = np.array([False] * self.nX)

    def __repr__(self):
        return f'Relay(U = {bool2int(self.U)}, Y = {bool2int(self.Y)}, X = {bool2int(self.X)})'
    
    def set_switch_in_vol(self, vol: bool):
        self.U[0] = vol
    
    def set_coil_high_vol(self, vol: bool):
        self.U[1] = vol
    
    def output(self):
        if self.X[0] == True: # coil is charged
            self.Y[0] = False
            self.Y[1] = self.U[0]
        else: # coil is discharged
            self.Y[0] = self.U[0]
            self.Y[1] = False
        
    def update(self):
        self.X[0] = self.U[1] # next coil voltage = current coil high voltage


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
