import unittest
import numpy as np
import matplotlib.pyplot as plt
from EStatus import *
from Util import *
from Device import Device
from Port import Port


class Split(Device):
    def __init__(self, name):
        self.le = Port('le', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        super().__init__(name)
    
    def __repr__(self):
        return f'Split(le = {self.le.status}, ru = {self.ru.status}, rd = {self.rd.status})'
    
    def calc_output(self):
        self.le.update_status()
        self.ru.status = self.le.status
        self.rd.status = self.le.status
    
    def update_state(self):
        pass # there is no state.

if __name__ == '__main__':
    pass

