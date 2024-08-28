import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Constant import *
from Util import *
from Device import Device
from Port import Port
from Source import Source
from Ground import Ground

class Relay(Device):
    def __init__(self, source=Source(), ground=Ground()):
        self.source = source
        self.ground = ground

        # U: input port, Y: output port, X: state vector
        self.nU = 2
        self.nY = 2
        self.nX = 1

        self.le = Port()
        self.up = Port()
        self.ru = Port()
        self.rd = Port()

        # # 0: switch in, 1: coil high
        # self.U = np.array([False] * self.nU)
        # # 0: switch out up, 1: switch out down
        # self.Y = np.array([False] * self.nY)
        # 0: actual coil voltage(considering delay)
        self.X = np.array([False] * self.nX)

        # self.Uc = [Device] * self.nU
        # self.Yc = [Device] * self.nY

    def __repr__(self):
        # return f'Relay(U = {bool2int(self.U)}, Y = {bool2int(self.Y)}, X = {bool2int(self.X)})'
        return f'Relay(up = {bool2int(self.up.volt)}, le = {bool2int(self.le.volt)}, ru = {bool2int(self.ru.volt)}, rd = {bool2int(self.rd.volt)})'
    
    def set_switch_in_vol(self, vol: bool):
        self.up.set_volt(vol)
    
    def set_coil_high_vol(self, vol: bool):
        self.le.set_volt(vol)
    
    # def append_to_input_port(index: int, device: Device):
    #     self.Uc[index] = device 
    
    # def append_to_output_port(index: int, device: Device):
    #     self.Yc[index] = device 
    
    def output(self):
        # if self.X[0] == True: # coil is charged
        #     self.Y[0] = False
        #     self.Y[1] = self.U[0]
        # else: # coil is discharged
        #     self.Y[0] = self.U[0]
        #     self.Y[1] = False
        if self.X[0] == True: # coil is charged
            self.ru.set_volt(False)
            self.rd.set_volt(self.up.volt)
        else: # coil is discharged
            self.ru.set_volt(self.up.volt)
            self.rd.set_volt(False)
        
        
    def update(self):
        # self.X[0] = self.U[1] # next coil voltage = current coil high voltage
        self.X[0] = self.le.volt # next coil voltage = current coil high voltage


if __name__ == '__main__':
    rly = Relay()
    print(rly)

    rly.set_switch_in_vol(True)

    rly.set_coil_high_vol(True)
    rly.output()
    print(rly)
    rly.update()
    rly.output()
    print(rly)
    rly.update()

    rly.set_coil_high_vol(False)
    rly.output()
    print(rly)
    rly.update()
    rly.output()
    print(rly)
    rly.update()