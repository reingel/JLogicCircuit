import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Source import Power

RelayValue = int
CHARGED = 1
DISCHARGED = 0

def rlystrof(v):
    if v == CHARGED:
        return 'CHARGED'
    elif v == DISCHARGED:
        return 'DISCHARGED'
    else:
        raise(RuntimeError)

class Relay(SimulatedCircuit):
    NORMAL = 0
    REVERSED = 1

    def __init__(self, name, parent, type=NORMAL):
        #  NORMAL  type: input(le, up)     -> output(ru, rd)
        # REVERSED type: input(le, ru, rd) -> output(up)
        self.parent = parent
        self.type = type

        # create ports
        self.le = Port('le', self)
        self.up = Port('up', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        # internal states
        self.X = DISCHARGED

        super().__init__('Relay', name)

    def __repr__(self):
        str = f'Relay({self.name}, le({strof(self.le.value)}) -> X({rlystrof(self.X)}), up({strof(self.up.value)}) -> ru({strof(self.ru.value)}) rd({strof(self.rd.value)})'
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
                self.ru.reset()
                self.rd.value = self.up.value
            else: # coil is discharged
                self.ru.value = self.up.value
                self.rd.reset()
        else: # REVERSED
            if self.X == HIGH: # coil is charged
                self.up.value = self.rd.value
            else: # coil is discharged
                self.up.value = self.ru.value
        
    def update_state(self):
        # next coil voltage = current coil high voltage
        if self.le.value == HIGH:
            self.X = CHARGED
        else: # GND or OPEN
            self.X = DISCHARGED

class TestRelay(unittest.TestCase):
    def test_relay_normal(self):
        print('test_relay_normal')

        tmp = SimulatedCircuit('SimulatedCircuit', 'tmp')
        pwr = Power('pwr')
        rly = Relay('rly', tmp, type=Relay.NORMAL)
        pwr.O >> rly.up

        pwr.power_on()
        pwr.step()

        rly.le.set()
        rly.step()
        self.assertEqual(rly.X, CHARGED)
        self.assertEqual(rly.ru.value, OPEN)
        self.assertEqual(rly.rd.value, rly.up.value)

        rly.le.reset()
        rly.step()
        self.assertEqual(rly.X, DISCHARGED)
        self.assertEqual(rly.ru.value, rly.up.value)
        self.assertEqual(rly.rd.value, OPEN)

    def test_relay_reversed(self):
        print('test_relay_reversed')

        tmp = SimulatedCircuit('SimulatedCircuit', 'tmp')
        pwr = Power('pwr')
        rly = Relay('rly_rvs', tmp, type=Relay.REVERSED)

        pwr.power_on()
        pwr.step()

        rly.le.reset()
        rly.ru.reset()
        rly.rd.set()
        rly.step()
        self.assertEqual(rly.X, DISCHARGED)
        self.assertEqual(rly.up.value, rly.ru.value)

        rly.le.set()
        rly.step()
        self.assertEqual(rly.X, CHARGED)
        self.assertEqual(rly.up.value, rly.rd.value)

        rly.le.reset()
        rly.ru.set()
        rly.rd.reset()
        rly.step()
        self.assertEqual(rly.X, DISCHARGED)
        self.assertEqual(rly.up.value, rly.ru.value)

        rly.le.set()
        rly.step()
        self.assertEqual(rly.X, CHARGED)
        self.assertEqual(rly.up.value, rly.rd.value)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestRelay('test_relay_normal'),
        TestRelay('test_relay_reversed'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
