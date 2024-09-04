import numpy as np
import matplotlib.pyplot as plt
from EStatus import *
from Util import *
from Device import Device
from Port import Port
from Source import Source
from Ground import Ground

class Relay(Device):
    def __init__(self, name, init_charge=OPEN):
        # create ports
        self.le = Port('le', self)
        self.up = Port('up', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        # internal states
        self.X = init_charge

        super().__init__(name)

    def __repr__(self):
        # return f'Relay(up = {bool2int(self.up.status)}, le = {bool2int(self.le.status)}, ru = {bool2int(self.ru.status)}, rd = {bool2int(self.rd.status)})'
        port_volts = np.array([self.le.status, self.up.status, self.ru.status, self.rd.status])
        return f'Relay({self.name}, [le up ru rd] = {bool2int(port_volts)}, X = {bool2int(self.X)})'
    
    def calc_output(self):
        self.up.update_status()
        self.le.update_status()
        if self.X == HIGH: # coil is charged
            self.ru.status = OPEN
            self.rd.status = self.up.status
        else: # coil is discharged
            self.ru.status = self.up.status
            self.rd.status = OPEN
        
        
    def update_state(self):
        self.X = self.le.status # next coil voltage = current coil high voltage


if __name__ == '__main__':
    rly = Relay('rly')
    rly.up.status = HIGH

    rly.le.status = HIGH
    rly.calc_output()
    print(rly)
    rly.update_state()
    rly.calc_output()
    print(rly)
    rly.update_state()

    rly.le.status = OPEN
    rly.calc_output()
    print(rly)
    rly.update_state()
    rly.calc_output()
    print(rly)
    rly.update_state()