import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Source import Power

class Relay(SimulatedCircuit):
    def __init__(self, name, parent, init_charge=OPEN):
        self.parent = parent

        # create ports
        self.le = Port('le', self)
        self.up = Port('up', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        # internal states
        self.X = init_charge

        super().__init__('Relay', name)

    def __repr__(self):
        str = f'Relay({self.name}, up = {self.up.value}, [X ru rd] = [{self.X} {self.ru.value} {self.rd.value}], le = {self.le.value})'
        # str += '\n'
        # str += f'  {self.ru}\n'
        # str += f'  {self.rd}\n'
        return str
    
    def update_inport(self):
        self.up.update_value()
        self.le.update_value()
    
    def calc_output(self):
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
        tmp = SimulatedCircuit('SimulatedCircuit', 'tmp')
        pwr = Power('pwr')
        rly = Relay('rly', tmp)
        pwr.out >> rly.up
        # rly.up.value = HIGH

        tmp.power_on()

        rly.le.value = HIGH
        rly.step()
        print(rly)
        rly.step()
        print(rly)

        rly.le.value = OPEN
        rly.step()
        print(rly)
        rly.step()
        print(rly)

if __name__ == '__main__':
    unittest.main()
