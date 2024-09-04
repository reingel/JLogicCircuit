import unittest
from EStatus import *
from Device import Device
from Power import Power
from Relay import Relay
from Junction import Junction

class Gate(Device):
    def __init__(self, name):
        super().__init__(name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, in = [{self.in1.status} {self.in2.status}], out = {self.out.status})'

    def set_input(self, v1: EStatus, v2: EStatus):
        if self.in1 and self.in2:
            self.in1.status = v1
            self.in2.status = v2
    
    def get_output(self):
        if self.out:
            return self.out.status

    def calc_output(self):
        for device in self.devices:
            device.calc_output()
        
    def update_state(self):
        for device in self.devices:
            device.update_state()


class And(Gate):
    def __init__(self, name):
        self.device_name = 'And'

        # creat devices
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1')
        self.rly2 = Relay('rly2')
        self.devices = [self.pwr, self.rly1, self.rly2]

        # connect
        self.pwr.ri >> self.rly1.up
        self.rly1.rd >> self.rly2.up

        # create access points
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.rly2.rd
    
        super().__init__(name)


class Or(Gate):
    def __init__(self, name):
        self.device_name = 'Or'

        # creat devices
        self.pwr1 = Power('pwr1')
        self.pwr2 = Power('pwr2')
        self.rly1 = Relay('rly1')
        self.rly2 = Relay('rly2')
        self.jnc = Junction('jnc')
        self.devices = [self.pwr1, self.pwr2, self.rly1, self.rly2, self.jnc]

        # connect
        self.pwr1.ri >> self.rly1.up
        self.pwr2.ri >> self.rly2.up
        self.rly1.rd >> self.jnc.lu
        self.rly2.rd >> self.jnc.ld

        # create access points
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.jnc.ri
    
        super().__init__(name)


class Nand(Gate):
    def __init__(self, name):
        self.device_name = 'Nand'

        # creat devices
        self.pwr1 = Power('pwr1')
        self.pwr2 = Power('pwr2')
        self.rly1 = Relay('rly1')
        self.rly2 = Relay('rly2')
        self.jnc = Junction('jnc')
        self.devices = [self.pwr1, self.pwr2, self.rly1, self.rly2, self.jnc]

        # connect
        self.pwr1.ri >> self.rly1.up
        self.pwr2.ri >> self.rly2.up
        self.rly1.ru >> self.jnc.lu
        self.rly2.ru >> self.jnc.ld

        # create access points
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.jnc.ri
    
        super().__init__(name)


class Nor(Gate):
    def __init__(self, name):
        self.device_name = 'Nor'

        # creat devices
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1')
        self.rly2 = Relay('rly2')
        self.devices = [self.pwr, self.rly1, self.rly2]

        # connect
        self.pwr.ri >> self.rly1.up
        self.rly1.ru >> self.rly2.up

        # create access points
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.rly2.ru
    
        super().__init__(name)


class Buffer(Gate):
    def __init__(self, name):
        self.device_name = 'Buffer'

        # creat devices
        self.pwr = Power('pwr')
        self.rly = Relay('rly')
        self.devices = [self.pwr, self.rly]

        # connect
        self.pwr.ri >> self.rly.up

        # create access points
        self.in1 = self.rly.le
        self.out = self.rly.rd
    
        super().__init__(name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, in = {self.in1.status}, out = {self.out.status})'

    def set_input(self, v1: EStatus):
        if self.in1:
            self.in1.status = v1


class Inverter(Gate):
    def __init__(self, name):
        self.device_name = 'Inverter'

        # creat devices
        self.pwr = Power('pwr')
        self.rly = Relay('rly')
        self.devices = [self.pwr, self.rly]

        # connect
        self.pwr.ri >> self.rly.up

        # create access points
        self.in1 = self.rly.le
        self.out = self.rly.ru
    
        super().__init__(name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, in = {self.in1.status}, out = {self.out.status})'

    def set_input(self, v1: EStatus):
        if self.in1:
            self.in1.status = v1


class TestGate(unittest.TestCase):
    def test_And(self):
        gate = And('and1')
        truth_table = [[OPEN, OPEN], [OPEN, HIGH]]
        for in1 in [OPEN, HIGH]:
            for in2 in [OPEN, HIGH]:
                gate.set_input(in1, in2)
                gate.step(n=2)
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[in1][in2])

    def test_Or(self):
        gate = Or('or1')
        truth_table = [[OPEN, HIGH], [HIGH, HIGH]]
        for in1 in [OPEN, HIGH]:
            for in2 in [OPEN, HIGH]:
                gate.set_input(in1, in2)
                gate.step(n=2)
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[in1][in2])

    def test_Nand(self):
        gate = Nand('nand1')
        truth_table = [[HIGH, HIGH], [HIGH, OPEN]]
        for in1 in [OPEN, HIGH]:
            for in2 in [OPEN, HIGH]:
                gate.set_input(in1, in2)
                gate.step(n=2)
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[in1][in2])

    def test_Nor(self):
        gate = Nor('nor1')
        truth_table = [[HIGH, OPEN], [OPEN, OPEN]]
        for in1 in [OPEN, HIGH]:
            for in2 in [OPEN, HIGH]:
                gate.set_input(in1, in2)
                gate.step(n=2)
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[in1][in2])

    def test_Buffer(self):
        gate = Buffer('buffer1')
        truth_table = [OPEN, HIGH]
        for in1 in [OPEN, HIGH]:
            gate.set_input(in1)
            gate.step(n=2)
            print(gate)
            self.assertEqual(gate.get_output(), truth_table[in1])

    def test_Inverter(self):
        gate = Inverter('inverter1')
        truth_table = [HIGH, OPEN]
        for in1 in [OPEN, HIGH]:
            gate.set_input(in1)
            gate.step(n=2)
            print(gate)
            self.assertEqual(gate.get_output(), truth_table[in1])




if __name__ == '__main__':
    unittest.main()