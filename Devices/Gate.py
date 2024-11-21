import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Source import Power
from Port import Port
from Relay import Relay
from Junction import Branch

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
        self.pwr.O >> self.rly1.up
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
        self.pwr.O >> self.rly[0].up
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
        self.brn = Branch('brn')
        self.O = Port('O', self)

        # connect
        self.pwr1.O >> self.rly1.up
        self.pwr2.O >> self.rly2.up
        self.rly1.rd >> self.brn
        self.rly2.rd >> self.brn
        self.brn >> self.O

        # create access points
        self.I0 = self.rly1.le
        self.I1 = self.rly2.le

        # update sequences
        self.update_sequence = [self.pwr1, self.pwr2, self.rly1, self.rly2, self.brn]
    
        super().__init__(self.device_name, name)

class OrN(Gate):
    def __init__(self, name, n):
        self.name = name
        if n < 3:
            raise(RuntimeError)
        self.n = n

        # creat elements
        self.pwr = Power('pwr')
        self.brnpw = Branch('brnpw')
        self.rly = [Relay(f'rly{i}', self) for i in range(self.n)]
        self.brno = Branch('brno')
        self.O = Port('O', self)

        # connect
        self.pwr.O >> self.brnpw
        for i in range(self.n):
            self.brnpw >> self.rly[i].up
            self.rly[i].rd >> self.brno
        self.brno >> self.O

        # update sequences
        self.update_sequence = [self.pwr, self.brnpw]
        self.update_sequence.extend([self.rly[i] for i in range(self.n)])
        self.update_sequence.append(self.brno)

        # create access points
        self.I = [self.rly[i].le for i in range(self.n)]
    
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
        self.pwr1.O >> self.rly1.up
        self.pwr2.O >> self.rly2.up
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
        self.pwr.O >> self.rly1.up
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
        self.pwr.O >> self.rly1.up
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
        self.pwr.O >> self.rly.up

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
        self.pwr.O >> self.rly.up

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
        print('test_And')

        gate = And('and1')
        gate.power_on()

        truth_table = [
            [[0, 0], 0],
            [[0, 1], 0],
            [[1, 0], 0],
            [[1, 1], 1],
        ]

        for i in range(len(truth_table)):
            gate.set_input(*truth_table[i][0])
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])

    def test_And4(self):
        print('test_And4')

        gate = AndN('andn', 4)
        gate.power_on()

        truth_table = [
            [[0, 0, 0, 0], 0],
            [[0, 0, 0, 1], 0],
            [[0, 0, 1, 0], 0],
            [[0, 0, 1, 1], 0],
            [[0, 1, 0, 0], 0],
            [[0, 1, 0, 1], 0],
            [[0, 1, 1, 0], 0],
            [[0, 1, 1, 1], 0],
            [[1, 0, 0, 0], 0],
            [[1, 0, 0, 1], 0],
            [[1, 0, 1, 0], 0],
            [[1, 0, 1, 1], 0],
            [[1, 1, 0, 0], 0],
            [[1, 1, 0, 1], 0],
            [[1, 1, 1, 0], 0],
            [[1, 1, 1, 1], 1],
        ]

        for i in range(len(truth_table)):
            for j in range(4):
                gate.I[j].value = truth_table[i][0][j]
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])

    
    def test_AndN_connected(self):
        print('test_AndN_connected')

        and1 = And('and')
        p1 = Port('p1', and1)
        p2 = Port('p2', and1)
        p3 = Port('p3', and1)
        p4 = Port('p4', and1)

        gate = AndN('andn', 4)
        self.assertEqual(gate.nconnected, 0)
        gate.I[0] >> p1
        self.assertEqual(gate.nconnected, 1)
        gate.I[1] >> p2
        self.assertEqual(gate.nconnected, 2)
        p3 >> gate.I[2]
        self.assertEqual(gate.nconnected, 3)
        p4 >> gate.I[3]
        self.assertEqual(gate.nconnected, 4)


    def test_Or(self):
        print('test_Or')

        gate = Or('or1')
        gate.power_on()

        truth_table = [
            [[0, 0], 0],
            [[0, 1], 1],
            [[1, 0], 1],
            [[1, 1], 1],
        ]

        for i in range(len(truth_table)):
            gate.set_input(*truth_table[i][0])
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])

    def test_OrN(self):
        print('test_OrN')

        n = 8
        gate = OrN('or8', n)
        gate.power_on()
        gate.step()

        for i in range(2**n):
            bin = f'{i:08b}'[::-1]
            for j in range(n):
                gate.I[j].value = int(bin[j])
            gate.step()
            self.assertEqual(gate.O.value, 1 if i > 0 else 0)

    def test_Nand(self):
        print('test_Nand')

        gate = Nand('nand1')
        gate.power_on()

        truth_table = [
            [[0, 0], 1],
            [[0, 1], 1],
            [[1, 0], 1],
            [[1, 1], 0],
        ]

        for i in range(len(truth_table)):
            gate.set_input(*truth_table[i][0])
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])

    def test_Nor(self):
        print('test_Nor')

        gate = Nor('nor1')
        gate.power_on()

        truth_table = [
            [[0, 0], 1],
            [[0, 1], 0],
            [[1, 0], 0],
            [[1, 1], 0],
        ]

        for i in range(len(truth_table)):
            gate.set_input(*truth_table[i][0])
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])

    def test_Xor(self):
        print('test_Xor')

        gate = Xor('xor1')
        gate.power_on()

        truth_table = [
            [[0, 0], 0],
            [[0, 1], 1],
            [[1, 0], 1],
            [[1, 1], 0],
        ]

        for i in range(len(truth_table)):
            gate.set_input(*truth_table[i][0])
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])


    def test_Buffer(self):
        print('test_Buffer')

        gate = Buffer('buffer1')
        gate.power_on()
    
        truth_table = [
            [0, 0],
            [1, 1],
        ]

        for i in range(len(truth_table)):
            gate.set_input(truth_table[i][0])
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])

    def test_TriStateBuffer(self):
        print('test_TriStateBuffer')

        gate = TriStateBuffer('tsb')
        gate.power_on()

        truth_table = [
            [0, 0],
            [1, 1],
        ]

        for i in range(len(truth_table)):
            gate.I.value = truth_table[i][0]
            gate.E.set()
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])
            gate.E.reset()
            gate.step()
            self.assertEqual(gate.get_output(), 0)

    def test_Inverter(self):
        print('test_Inverter')

        gate = Inverter('inverter1')
        gate.power_on()
    
        truth_table = [
            [0, 1],
            [1, 0],
        ]

        for i in range(len(truth_table)):
            gate.set_input(truth_table[i][0])
            gate.step()
            self.assertEqual(gate.get_output(), truth_table[i][1])

    def test_AndOr(self):
        print('test_AndOr')

        and1 = And('and1')
        and2 = And('and2')
        or1 = Or('or1')
        and1.power_on()
        and2.power_on()
        or1.power_on()

        and1.O >> or1.I0
        and2.O >> or1.I1

        truth_table = [
            [[0, 0, 0, 0], 0],
            [[0, 0, 0, 1], 0],
            [[0, 0, 1, 0], 0],
            [[0, 0, 1, 1], 1],
            [[0, 1, 0, 0], 0],
            [[0, 1, 0, 1], 0],
            [[0, 1, 1, 0], 0],
            [[0, 1, 1, 1], 1],
            [[1, 0, 0, 0], 0],
            [[1, 0, 0, 1], 0],
            [[1, 0, 1, 0], 0],
            [[1, 0, 1, 1], 1],
            [[1, 1, 0, 0], 1],
            [[1, 1, 0, 1], 1],
            [[1, 1, 1, 0], 1],
            [[1, 1, 1, 1], 1],
        ]

        for i in range(len(truth_table)):
            and1.I0.value = truth_table[i][0][0]
            and1.I1.value = truth_table[i][0][1]
            and2.I0.value = truth_table[i][0][2]
            and2.I1.value = truth_table[i][0][3]
            and1.step()
            and2.step()
            or1.step()
            self.assertEqual(or1.O.value, truth_table[i][1])




if __name__ == '__main__':
    unittest.main()