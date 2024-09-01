import numpy as np
import matplotlib.pyplot as plt
from BitValue import *
from Util import *
from Device import Device
from Port import Port
from Source import Source
from Ground import Ground

class Relay(Device):
    def __init__(self, name, init_charge=LOW):
        # create ports
        self.le = Port('le', self)
        self.up = Port('up', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        # internal states
        self.X = init_charge

        super().__init__(name)

    def __repr__(self):
        # return f'Relay(up = {bool2int(self.up.value)}, le = {bool2int(self.le.value)}, ru = {bool2int(self.ru.value)}, rd = {bool2int(self.rd.value)})'
        port_volts = np.array([self.le.value, self.up.value, self.ru.value, self.rd.value])
        return f'Relay({self.name}, [le up ru rd] = {bool2int(port_volts)}, X = {bool2int(self.X)})'
    
    def calc_output(self):
        self.up.update()
        self.le.update()
        if self.X == HIGH: # coil is charged
            self.ru.set_value(LOW)
            self.rd.set_value(self.up.value)
        else: # coil is discharged
            self.ru.set_value(self.up.value)
            self.rd.set_value(LOW)
        
        
    def update(self):
        self.X = self.le.value # next coil voltage = current coil high voltage


if __name__ == '__main__':
    rly = Relay('rly')
    rly.up.set_value(HIGH)

    rly.le.set_value(HIGH)
    rly.calc_output()
    print(rly)
    rly.update()
    rly.calc_output()
    print(rly)
    rly.update()

    rly.le.set_value(LOW)
    rly.calc_output()
    print(rly)
    rly.update()
    rly.calc_output()
    print(rly)
    rly.update()