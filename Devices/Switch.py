import numpy as np
import matplotlib.pyplot as plt
from EStatus import *
from Util import *
from Device import Device
from Port import Port
from Source import Source
from Ground import Ground
from Relay import Relay

class Switch(Device):
    def __init__(self, name):
        self.__state = OPEN # open

        self.le = Port('le', self)
        self.ri = Port('ri', self)

        super().__init__(name)
    
    def __repr__(self):
        return f'Switch(state = {bool2int(self.state)}, le = {self.le}, ri = {self.ri})'
    
    @property
    def state(self):
        return self.__state
    
    def invert(self):
        self.__state = not self.state
    
    def set_state(self, state):
        self.__state = state
    
    def calc_output(self):
        self.le.update_status()
        if self.state: # switch on
            self.ri.status = self.le.status
        else: # switch off
            self.ri.status = OPEN
    
    def update_state(self):
        pass # there is no state.

if __name__ == '__main__':
    sw = Switch('sw1')
    src = Source('src1')
    sw.le.connect(src.ri)
    print(sw)
    sw.invert()
    print(sw)
    sw.set_state(OPEN)
    print(sw)
