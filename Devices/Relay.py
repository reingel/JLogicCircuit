import unittest
from BitValue import *
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
        return f'Relay({self.name}, up = {self.up.value}, [X ru rd] = [{self.X} {self.ru.value} {self.rd.value}], le = {self.le.value})'
    
    def calc_output(self):
        self.up.update_status()
        self.le.update_status()
        if self.X == HIGH: # coil is charged
            self.ru.value = OPEN
            self.rd.value = self.up.value
        else: # coil is discharged
            self.ru.value = self.up.value
            self.rd.value = OPEN
        
    def update_state(self):
        self.X = self.le.value # next coil voltage = current coil high voltage

class TestRelay(unittest.TestCase):
    def test_relay(self):
        rly = Relay('rly')
        rly.up.value = HIGH

        rly.le.value = HIGH
        rly.calc_output()
        print(rly)
        rly.update_state()
        rly.calc_output()
        print(rly)
        rly.update_state()

        rly.le.value = OPEN
        rly.calc_output()
        print(rly)
        rly.update_state()
        rly.calc_output()
        print(rly)
        rly.update_state()

if __name__ == '__main__':
    unittest.main()
