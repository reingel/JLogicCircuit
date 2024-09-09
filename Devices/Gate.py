import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Source import Power
from Relay import Relay
from Junction import Merge

class Gate(SimulatedCircuit):
    def __init__(self, device_name, name):
        super().__init__(device_name, name)
    
    def __repr__(self):
        str = f'   {self.device_name}({self.name}, [{self.in1.value} {self.in2.value}] -> {self.out.value})'
        # str += '\n'
        # for device in self.subdevices:
        #     str += f'      {device}\n'
        return str

    def set_input(self, v1: BitValue, v2: BitValue):
        if self.in1 and self.in2:
            self.in1.value = v1
            self.in2.value = v2
    
    def get_output(self):
        if self.out:
            return self.out.value


class And(Gate):
    def __init__(self, name):
        self.device_name = 'And'

        # creat subdevices
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)

        # connect
        self.pwr.ri >> self.rly1.up
        self.rly1.rd >> self.rly2.up

        # create access points
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.rly2.rd

        # update sequences
        self.inports = [self.in1, self.in2]
        self.subdevices = [self.pwr, self.rly1, self.rly2]
    
        super().__init__('And', name)


class Or(Gate):
    def __init__(self, name):
        self.device_name = 'Or'

        # creat subdevices
        self.pwr1 = Power('pwr1')
        self.pwr2 = Power('pwr2')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)
        self.jnc = Merge('jnc')

        # connect
        self.pwr1.ri >> self.rly1.up
        self.pwr2.ri >> self.rly2.up
        self.rly1.rd >> self.jnc.lu
        self.rly2.rd >> self.jnc.ld

        # create access points
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.jnc.ri

        # update sequences
        self.inports = [self.in1, self.in2]
        self.subdevices = [self.pwr1, self.pwr2, self.rly1, self.rly2, self.jnc]
    
        super().__init__('Or', name)


class Nand(Gate):
    def __init__(self, name):
        self.device_name = 'Nand'

        # creat subdevices
        self.pwr1 = Power('pwr1')
        self.pwr2 = Power('pwr2')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)
        self.jnc = Merge('jnc')

        # connect
        self.pwr1.ri >> self.rly1.up
        self.pwr2.ri >> self.rly2.up
        self.rly1.ru >> self.jnc.lu
        self.rly2.ru >> self.jnc.ld

        # create access points
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.jnc.ri

        # update sequences
        self.inports = [self.in1, self.in2]
        self.subdevices = [self.pwr1, self.pwr2, self.rly1, self.rly2, self.jnc]
    
        super().__init__('Nand', name)


class Nor(Gate):
    def __init__(self, name):
        self.device_name = 'Nor'

        # creat subdevices
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)

        # connect
        self.pwr.ri >> self.rly1.up
        self.rly1.ru >> self.rly2.up

        # create access points
        self.in1 = self.rly1.le
        self.in2 = self.rly2.le
        self.out = self.rly2.ru

        # update sequences
        self.inports = [self.in1, self.in2]
        self.subdevices = [self.pwr, self.rly1, self.rly2]
    
        super().__init__('Nor', name)


class Buffer(Gate):
    def __init__(self, name):
        self.device_name = 'Buffer'

        # creat subdevices
        self.pwr = Power('pwr')
        self.rly = Relay('rly', self)

        # connect
        self.pwr.ri >> self.rly.up

        # create access points
        self.in1 = self.rly.le
        self.out = self.rly.rd

        # update sequences
        self.inports = [self.in1]
        self.subdevices = [self.pwr, self.rly]
    
        super().__init__('Buffer', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {self.in1.value} -> {self.out.value})'

    def set_input(self, v1: BitValue):
        if self.in1:
            self.in1.value = v1


class Inverter(Gate):
    def __init__(self, name):
        self.device_name = 'Inverter'

        # creat subdevices
        self.pwr = Power('pwr')
        self.rly = Relay('rly', self)

        # connect
        self.pwr.ri >> self.rly.up

        # create access points
        self.in1 = self.rly.le
        self.out = self.rly.ru

        # update sequences
        self.inports = [self.in1]
        self.subdevices = [self.pwr, self.rly]
    
        super().__init__('Inverter', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {self.in1.value} -> {self.out.value})'

    def set_input(self, v1: BitValue):
        if self.in1:
            self.in1.value = v1


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
    
    def test_AndOr(self):
        and1 = And('and1')
        and2 = And('and2')
        or1 = Or('or1')
        and1.out >> or1.in1
        and2.out >> or1.in2

        and1.in1.value = OPEN
        and1.in2.value = HIGH
        and2.in1.value = HIGH
        and2.in2.value = HIGH

        for i in range(2):
            and1.step()
            and2.step()
            or1.step()

        print(and1)
        print(and2)
        print(or1)





if __name__ == '__main__':
    unittest.main()