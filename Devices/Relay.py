import numpy as np
import matplotlib.pyplot as plt
from Constant import *
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
        # return f'Relay(up = {bool2int(self.up.volt)}, le = {bool2int(self.le.volt)}, ru = {bool2int(self.ru.volt)}, rd = {bool2int(self.rd.volt)})'
        port_volts = np.array([self.le.volt, self.up.volt, self.ru.volt, self.rd.volt])
        return f'Relay({self.name}, [le up ru rd] = {bool2int(port_volts)}, X = {bool2int(self.X)})'
    
    def calc_output(self):
        self.up.update()
        self.le.update()
        if self.X == HIGH: # coil is charged
            self.ru.set_volt(LOW)
            self.rd.set_volt(self.up.volt)
        else: # coil is discharged
            self.ru.set_volt(self.up.volt)
            self.rd.set_volt(LOW)
        
        
    def update(self):
        self.X = self.le.volt # next coil voltage = current coil high voltage


if __name__ == '__main__':
    rly = Relay('rly')
    rly.up.set_volt(HIGH)

    rly.le.set_volt(HIGH)
    rly.calc_output()
    print(rly)
    rly.update()
    rly.calc_output()
    print(rly)
    rly.update()

    rly.le.set_volt(LOW)
    rly.calc_output()
    print(rly)
    rly.update()
    rly.calc_output()
    print(rly)
    rly.update()