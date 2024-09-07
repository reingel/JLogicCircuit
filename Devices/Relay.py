import unittest
from EStatus import *
from Device import Device
from Port import Port
from Source import Power

class Relay(Device):
    def __init__(self, name, init_charge=OPEN):
        # create ports
        self.le = Port('le', self)
        self.up = Port('up', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        # internal states
        self.X = init_charge

        super().__init__('Relay', name)

    def __repr__(self):
        return f'Relay({self.name}, up = {self.up.status}, [X ru rd] = [{self.X} {self.ru.status} {self.rd.status}], le = {self.le.status})'
    
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

class TestRelay(unittest.TestCase):
    def test_relay(self):
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

if __name__ == '__main__':
    unittest.main()
