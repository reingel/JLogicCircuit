import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Source import Power
from Port import Port
from Relay import Relay
from Junction import Branch, Merge

class Gate(SimulatedCircuit):
    def __init__(self, device_name, name):
        super().__init__(device_name, name)
    
    def __repr__(self):
        if hasattr(self, 'I0') and hasattr(self, 'I1'):
            str = f'{self.device_name}({self.name}, [{strof(self.I0.value)} {strof(self.I1.value)}] -> {strof(self.O.value)})'
            # str += '\n'
            # str += '  ' + self.rly1.__repr__() + '\n'
            # str += '  ' + self.rly2.__repr__()
            return str

    def set_input(self, v0: BitValue, v1: BitValue):
        if self.I0 and self.I1:
            self.I0.value = v0
            self.I1.value = v1
    
    def get_output(self):
        if self.O:
            return self.O.value


class And(Gate):
    def __init__(self, name):
        self.device_name = 'And'

        # creat update_sequence
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)

        # connect
        self.pwr.ri >> self.rly1.up
        self.rly1.rd >> self.rly2.up

        # create access points
        self.I0 = self.rly1.le
        self.I1 = self.rly2.le
        self.O = self.rly2.rd

        # update sequences
        self.update_sequence = [self.pwr, self.rly1, self.rly2]
    
        super().__init__(self.device_name, name)

class AndN(Gate):
    def __init__(self, name, n):
        self.name = name
        if n < 3:
            raise(RuntimeError)
        self.n = n

        # create update_sequence
        self.pwr = Power('pwr')
        self.rly = [Relay(f'rly{i}', self) for i in range(self.n)]
        self.I = []

        self.update_sequence = [self.pwr]

        # connect
        self.pwr.ri >> self.rly[0].up
        for i in range(self.n - 1):
            self.rly[i].rd >> self.rly[i + 1].up
            self.I.append(self.rly[i].le)
            self.update_sequence.append(self.rly[i])
        self.I.append(self.rly[self.n - 1].le)
        self.update_sequence.append(self.rly[self.n - 1])

        # create access points
        self.O = self.rly[self.n - 1].rd
    
        super().__init__('AndN', name)

    def __repr__(self):
        str = f'{self.device_name}({self.name}({self.n}), {[strof(self.I[i].value) for i in range(self.n)]} -> {strof(self.O.value)})'
        return str
    
    @property
    def nconnected(self):
        n = 0
        for i in range(self.n):
            if self.I[i].connected:
                n += 1
        return n

class Or(Gate):
    def __init__(self, name):
        self.device_name = 'Or'

        # creat update_sequence
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
        self.I0 = self.rly1.le
        self.I1 = self.rly2.le
        self.O = self.jnc.ri

        # update sequences
        self.update_sequence = [self.pwr1, self.pwr2, self.rly1, self.rly2, self.jnc]
    
        super().__init__(self.device_name, name)

class OrN(Gate):
    def __init__(self, name, n):
        self.name = name
        if n < 3:
            raise(RuntimeError)
        self.n = n

        # creat update_sequence
        self.pwr = [Power(f'pwr{i}') for i in range(self.n)]
        self.rly = [Relay(f'rly{i}', self) for i in range(self.n)]
        self.mrg = [Merge(f'mrg{i}') for i in range(self.n - 1)]
        self.I = []

        self.update_sequence = []

        # connect
        for i in range(self.n):
            self.pwr[i].ri >> self.rly[i].up
            self.I.append(self.rly[i].le)
            self.update_sequence.append(self.pwr[i])
            self.update_sequence.append(self.rly[i])
        self.rly[0].rd >> self.mrg[0].lu
        for i in range(self.n - 2):
            self.rly[i+1].rd >> self.mrg[i].ld
            self.mrg[i].ri >> self.mrg[i+1].lu
            # update sequences
            self.update_sequence.append(self.mrg[i])
        self.rly[self.n - 1].rd >> self.mrg[self.n - 2].ld

        # update sequences
        self.update_sequence.append(self.mrg[self.n - 2])

        # create access points
        self.O = self.mrg[self.n - 2].ri
    
        super().__init__('OrN', name)

    def __repr__(self):
        str = f'{self.device_name}({self.name}, I = {[self.I[i].value for i in range(self.n)]} -> {self.O.value})'
        return str


class Nand(Gate):
    def __init__(self, name):
        self.device_name = 'Nand'

        # creat elements
        self.pwr1 = Power('pwr1')
        self.pwr2 = Power('pwr2')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)
        self.brn = Branch('brn')
        self.O = Port('O', self)

        # connect
        self.pwr1.ri >> self.rly1.up
        self.pwr2.ri >> self.rly2.up
        self.brn.add_inport(self.rly1.ru)
        self.brn.add_inport(self.rly2.ru)
        self.brn.add_outport(self.O)

        # create access points
        self.I0 = self.rly1.le
        self.I1 = self.rly2.le

        # update sequences
        self.update_sequence = [self.pwr1, self.pwr2, self.rly1, self.rly2, self.brn]
    
        super().__init__(self.device_name, name)


class Nor(Gate):
    def __init__(self, name):
        self.device_name = 'Nor'

        # creat update_sequence
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)

        # connect
        self.pwr.ri >> self.rly1.up
        self.rly1.ru >> self.rly2.up

        # create access points
        self.I0 = self.rly1.le
        self.I1 = self.rly2.le
        self.O = self.rly2.ru

        # update sequences
        self.update_sequence = [self.pwr, self.rly1, self.rly2]
    
        super().__init__(self.device_name, name)


class Xor(Gate):
    def __init__(self, name):
        self.device_name = 'Xor'

        # creat update_sequence
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self, type=Relay.REVERSED)

        # connect
        self.pwr.ri >> self.rly1.up
        self.rly1.ru >> self.rly2.rd
        self.rly1.rd >> self.rly2.ru

        # create access points
        self.I0 = self.rly1.le
        self.I1 = self.rly2.le
        self.O = self.rly2.up

        # update sequences
        self.update_sequence = [self.pwr, self.rly1, self.rly2]
    
        super().__init__(self.device_name, name)


class Buffer(Gate):
    def __init__(self, name):
        self.device_name = 'Buffer'

        # creat update_sequence
        self.pwr = Power('pwr')
        self.rly = Relay('rly', self)

        # connect
        self.pwr.ri >> self.rly.up

        # create access points
        self.I = self.rly.le
        self.O = self.rly.rd

        # update sequences
        self.update_sequence = [self.pwr, self.rly]
    
        super().__init__(self.device_name, name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {strof(self.I.value)} -> {strof(self.O.value)})'

    def set_input(self, v1: BitValue):
        if self.I:
            self.I.value = v1

class TriStateBuffer(Gate):
    def __init__(self, name):
        self.device_name = 'TriStateBuffer'
        self.name = name

        # creat update_sequence
        self.rly = Relay('rly', self)

        # create access points
        self.E = self.rly.le
        self.I = self.rly.up
        self.O = self.rly.rd

        # update sequences
        self.update_sequence = [self.rly]
    
        super().__init__(self.device_name, name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {strof(self.E.value)}: {strof(self.I.value)} -> {strof(self.O.value)})'


class Inverter(Gate):
    def __init__(self, name):
        self.device_name = 'Inverter'

        # creat update_sequence
        self.pwr = Power('pwr')
        self.rly = Relay('rly', self)

        # connect
        self.pwr.ri >> self.rly.up

        # create access points
        self.I = self.rly.le
        self.O = self.rly.ru

        # update sequences
        self.update_sequence = [self.pwr, self.rly]
    
        super().__init__(self.device_name, name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {strof(self.I.value)} -> {strof(self.O.value)})'

    def set_input(self, v1: BitValue):
        if self.I:
            self.I.value = v1


class TestGate(unittest.TestCase):
    def test_And(self):
        gate = And('and1')
        gate.power_on()
        truth_table = [[OPEN, OPEN], [OPEN, HIGH]]
        for v0 in [OPEN, HIGH]:
            for v1 in [OPEN, HIGH]:
                gate.set_input(v0, v1)
                gate.step()
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[v0][v1])

    def test_And4(self):
        print('And4')
        gate = AndN('andn', 4)
        gate.power_on()
        truth_table = [[[[OPEN, OPEN], [OPEN, OPEN]], [[OPEN, OPEN], [OPEN, OPEN]]], [[[OPEN, OPEN], [OPEN, OPEN]], [[OPEN, OPEN], [OPEN, HIGH]]]]
        for v0 in [OPEN, HIGH]:
            for v1 in [OPEN, HIGH]:
                for v2 in [OPEN, HIGH]:
                    for v3 in [OPEN, HIGH]:
                        gate.I[0].value = v0
                        gate.I[1].value = v1
                        gate.I[2].value = v2
                        gate.I[3].value = v3
                        gate.step()
                        print(gate)
                        self.assertEqual(gate.O.value, truth_table[v0][v1][v2][v3])
    
    def test_AndN_connected(self):
        and1 = And('and')
        p1 = Port('p1', and1)
        p2 = Port('p2', and1)
        p3 = Port('p3', and1)
        p4 = Port('p4', and1)

        print('test_AndN_connected')
        gate = AndN('andn', 4)
        print(gate.nconnected)
        gate.I[0] >> p1
        print(gate.nconnected)
        gate.I[1] >> p2
        print(gate.nconnected)
        p3 >> gate.I[2]
        print(gate.nconnected)
        p4 >> gate.I[3]
        print(gate.nconnected)


    def test_Or(self):
        gate = Or('or1')
        gate.power_on()
        truth_table = [[OPEN, HIGH], [HIGH, HIGH]]
        for v0 in [OPEN, HIGH]:
            for v1 in [OPEN, HIGH]:
                gate.set_input(v0, v1)
                gate.step()
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[v0][v1])

    def test_OrN(self):
        gate = OrN('or8', 8)
        gate.power_on()
        gate.step()
        print(gate.O.value)
        for i in range(8):
            gate.I[i].value = HIGH
            gate.step()
            print(gate.O.value)
            gate.I[i].value = OPEN
            gate.step()
            print(gate.O.value)

    def test_Nand(self):
        gate = Nand('nand1')
        gate.power_on()
        truth_table = [[HIGH, HIGH], [HIGH, OPEN]]
        for v0 in [OPEN, HIGH]:
            for v1 in [OPEN, HIGH]:
                gate.set_input(v0, v1)
                gate.step()
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[v0][v1])

    def test_Nor(self):
        gate = Nor('nor1')
        gate.power_on()
        truth_table = [[HIGH, OPEN], [OPEN, OPEN]]
        for v0 in [OPEN, HIGH]:
            for v1 in [OPEN, HIGH]:
                gate.set_input(v0, v1)
                gate.step()
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[v0][v1])

    def test_Buffer(self):
        gate = Buffer('buffer1')
        gate.power_on()
        truth_table = [OPEN, HIGH]
        for v0 in [OPEN, HIGH]:
            gate.set_input(v0)
            gate.step()
            print(gate)
            self.assertEqual(gate.get_output(), truth_table[v0])
    
    def test_TriStateBuffer(self):
        gate = TriStateBuffer('tsb')
        gate.power_on()
        truth_table = [[OPEN, OPEN], [OPEN, HIGH]]
        for e in [OPEN, HIGH]:
            for i in [OPEN, HIGH]:
                gate.E.value = e
                gate.I.value = i
                gate.step()
                print(gate)
                self.assertEqual(gate.O.value, truth_table[e][i])

    def test_Inverter(self):
        gate = Inverter('inverter1')
        gate.power_on()
        truth_table = [HIGH, OPEN]
        for v0 in [OPEN, HIGH]:
            gate.set_input(v0)
            gate.step()
            print(gate)
            self.assertEqual(gate.get_output(), truth_table[v0])
    
    def test_AndOr(self):
        and1 = And('and1')
        and2 = And('and2')
        or1 = Or('or1')
        and1.power_on()
        and2.power_on()
        or1.power_on()

        and1.O >> or1.I0
        and2.O >> or1.I1

        and1.I0.value = OPEN
        and1.I1.value = HIGH
        and2.I0.value = HIGH
        and2.I1.value = HIGH

        for i in range(1):
            and1.step()
            and2.step()
            or1.step()

        print(and1)
        print(and2)
        print(or1)

    def test_Xor(self):
        gate = Xor('xor1')
        gate.power_on()
        truth_table = [[OPEN, HIGH], [HIGH, OPEN]]
        for v0 in [OPEN, HIGH]:
            for v1 in [OPEN, HIGH]:
                gate.set_input(v0, v1)
                gate.step()
                print(gate)
                self.assertEqual(gate.get_output(), truth_table[v0][v1])





if __name__ == '__main__':
    unittest.main()