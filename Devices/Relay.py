import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Source import Power

class Relay(SimulatedCircuit):
    NORMAL = 0
    REVERSED = 1

    def __init__(self, name, parent, type=NORMAL):
        self.parent = parent
        self.type = type

        # create ports
        self.le = Port('le', self)
        self.up = Port('up', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        # internal states
        self.X = OPEN

        super().__init__('Relay', name)

    def __repr__(self):
        str = f'Relay({self.name}, up = {self.up.value}, [X ru rd] = [{self.X} {self.ru.value} {self.rd.value}], le = {self.le.value})'
        # str += '\n'
        # str += f'  {self.ru}\n'
        # str += f'  {self.rd}\n'
        return str
    
    def update_inport(self):
        if self.type == self.NORMAL:
            self.up.update_value()
            self.le.update_value()
        else: # REVERSED
            self.le.update_value()
            self.ru.update_value()
            self.rd.update_value()
    
    def calc_output(self):
        if self.type == self.NORMAL:
            if self.X == HIGH: # coil is charged
                self.ru.value = OPEN
                self.rd.value = self.up.value
            else: # coil is discharged
                self.ru.value = self.up.value
                self.rd.value = OPEN
        else: # REVERSED
            if self.X == HIGH: # coil is charged
                self.up.value = self.rd.value
            else: # coil is discharged
                self.up.value = self.ru.value
        
    def update_state(self):
        self.X = self.le.value # next coil voltage = current coil high voltage

class TestRelay(unittest.TestCase):
    def test_relay(self):
        tmp = SimulatedCircuit('SimulatedCircuit', 'tmp')
        pwr = Power('pwr')
        rly = Relay('rly', tmp)
        pwr.out >> rly.up

        pwr.power_on()
        pwr.step()

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

    def test_relay_reserved(self):
        tmp = SimulatedCircuit('SimulatedCircuit', 'tmp')
        pwr = Power('pwr')
        rly = Relay('rly_rvs', tmp, type=Relay.NORMAL)
        pwr.out >> rly.up

        pwr.power_on()
        pwr.step()

        rly.ru.value = OPEN
        rly.rd.value = HIGH
        rly.le.value = OPEN
        rly.step()
        print(rly)
        rly.le.value = HIGH
        rly.step()
        print(rly)

        rly.ru.value = HIGH
        rly.rd.value = OPEN
        rly.le.value = OPEN
        rly.step()
        print(rly)
        rly.le.value = HIGH
        rly.step()
        print(rly)

if __name__ == '__main__':
    unittest.main()
