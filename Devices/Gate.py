from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Relay import Relay
from Source import Power
from Branch import Branch
from collections.abc import Iterable
from Util import i2bi


class AndN(SimulatedCircuit):
    '''
    n: no. of inputs
    I: Input signal vector (n x 1)
    O: Output signal (HIGH or OPEN)
    '''
    def __init__(self, name, n):
        self.device_name = 'And'
        self.name = name
        self.n = n
        self._nconnected = 0
        self._outconnected = False

        # elements
        self.pwr = Power('pwr')
        self.rly = [Relay(f'rly{i}', self) for i in range(self.n)]

        # connections
        self.pwr.O >> self.rly[0].up
        for i in range(self.n - 1):
            self.rly[i].rd >> self.rly[i + 1].up

        # access points
        self.I = [self.rly[i].le for i in range(self.n)]
        self.O = self.rly[-1].rd

        # update sequence
        self.update_sequence = [self.pwr]
        self.update_sequence.extend([self.rly[i] for i in range(self.n)])
    
        super().__init__(self.device_name, self.name)
    
    @property
    def nconnected(self):
        return self._nconnected
    
    def connect_input(self, obj):
        if isinstance(obj, Iterable):
            for p in obj:
                self.connect_input(p)
            return self
        elif isinstance(obj, Port) or isinstance(obj, Branch):
            i = self.nconnected
            if i >= self.n:
                raise(RuntimeError)
            obj >> self.I[i]
            self._nconnected += 1
            return self
        elif hasattr(obj, 'O') and (isinstance(obj.O, Port) or isinstance(obj.O, Branch)):
            return self.connect_input(obj.O)
        else:
            raise(RuntimeError)
    
    def connect_output(self, obj):
        if isinstance(obj, Iterable):
            for p in obj:
                self.connect_output(p)
            return self
        elif isinstance(obj, Port) or isinstance(obj, Branch):
            if self._outconnected:
                raise(RuntimeError)
            self.O >> obj
            self._outconnected = True
            return self
        elif hasattr(obj, 'O') and (isinstance(obj.I, Port) or isinstance(obj.I, Branch)):
            return self.connect_output(obj.I)
        else:
            raise(RuntimeError)
    
    def __lshift__(self, obj):
        return self.connect_input(obj)

    def __rshift__(self, obj):
        return self.connect_output(obj)

    def __rrshift__(self, obj):
        return self.connect_input(obj)
    

class And(AndN):
    def __init__(self, name):
        super().__init__(name, 2)


class OrN(SimulatedCircuit):
    def __init__(self, name, n):
        self.device_name = 'Or'
        self.name = name
        self.n = n

        # creat elements
        self.pwr = Power('pwr')
        self.brnpw = Branch('brnpw')
        self.rly = [Relay(f'rly{i}', self) for i in range(self.n)]
        self.brn = Branch('brn')

        # connect
        self.pwr.O >> self.brnpw
        for i in range(self.n):
            self.brnpw >> self.rly[i].up
            self.rly[i].rd >> self.brn

        # create access points
        self.I = [self.rly[i].le for i in range(self.n)]
        self.O = self.brn

        # update sequences
        self.update_sequence = [self.pwr, self.brnpw]
        self.update_sequence.extend([self.rly[i] for i in range(self.n)])
        self.update_sequence.append(self.brn)
    
        super().__init__(self.device_name, name)


class Or(OrN):
    def __init__(self, name):
        super().__init__(name, 2)


class Nand(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'Nand'
        self.name = name

        # creat elements
        self.pwr1 = Power('pwr1')
        self.pwr2 = Power('pwr2')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)
        self.brn = Branch('brn')

        # connect
        self.pwr1.O >> self.rly1.up
        self.pwr2.O >> self.rly2.up
        self.rly1.ru >> self.brn
        self.rly2.ru >> self.brn

        # create access points
        self.I = [self.rly1.le, self.rly2.le]
        self.O = self.brn

        # update sequences
        self.update_sequence = [self.pwr1, self.pwr2, self.rly1, self.rly2, self.brn]
    
        super().__init__(self.device_name, name)


class Nor(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'Nor'
        self.name = name

        # creat update_sequence
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self)

        # connect
        self.pwr.O >> self.rly1.up
        self.rly1.ru >> self.rly2.up

        # create access points
        self.I = [self.rly1.le, self.rly2.le]
        self.O = self.rly2.ru

        # update sequences
        self.update_sequence = [self.pwr, self.rly1, self.rly2]
    
        super().__init__(self.device_name, name)


class Xor(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'Xor'
        self.name = name

        # creat update_sequence
        self.pwr = Power('pwr')
        self.rly1 = Relay('rly1', self)
        self.rly2 = Relay('rly2', self, type=Relay.REVERSED)

        # connect
        self.pwr.O >> self.rly1.up
        self.rly1.ru >> self.rly2.rd
        self.rly1.rd >> self.rly2.ru

        # create access points
        self.I = [self.rly1.le, self.rly2.le]
        self.O = self.rly2.up

        # update sequences
        self.update_sequence = [self.pwr, self.rly1, self.rly2]
    
        super().__init__(self.device_name, name)


class Buffer(SimulatedCircuit):
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

    # def __rshift__(self, obj):
    #     if isinstance(obj, Port) or isinstance(obj, Branch):
    #         self.O >> obj
    #         return obj
    #     else:
    #         return self.O
    
    def set_input(self, v1: BitValue):
        if self.I:
            self.I.value = v1


class TriStateBuffer(SimulatedCircuit):
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


class Inverter(SimulatedCircuit):
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



import unittest

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
            for j in range(2):
                gate.I[j].value = truth_table[i][0][j]
            gate.step()
            self.assertEqual(gate.O.value, truth_table[i][1])

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
            self.assertEqual(gate.O.value, truth_table[i][1])

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
            for j in range(2):
                gate.I[j].value = truth_table[i][0][j]
            gate.step()
            self.assertEqual(gate.O.value, truth_table[i][1])

    def test_OrN(self):
        print('test_OrN')

        n = 8
        gate = OrN('or8', n)
        gate.power_on()
        gate.step()

        for i in range(2**n):
            bin = i2bi(i, 8)
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
            for j in range(2):
                gate.I[j].value = truth_table[i][0][j]
            gate.step()
            self.assertEqual(gate.O.value, truth_table[i][1])

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
            for j in range(2):
                gate.I[j].value = truth_table[i][0][j]
            gate.step()
            self.assertEqual(gate.O.value, truth_table[i][1])

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
            for j in range(2):
                gate.I[j].value = truth_table[i][0][j]
            gate.step()
            self.assertEqual(gate.O.value, truth_table[i][1])

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
            self.assertEqual(gate.O.value, truth_table[i][1])

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
            self.assertEqual(gate.O.value, truth_table[i][1])
            gate.E.reset()
            gate.step()
            self.assertEqual(gate.O.value, 0)

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
            self.assertEqual(gate.O.value, truth_table[i][1])

    def test_AndOr(self):
        print('test_AndOr')

        and1 = And('and1')
        and2 = And('and2')
        or1 = Or('or1')
        and1 >> or1.I[0]
        and2 >> or1.I[1]
        and1.power_on()
        and2.power_on()
        or1.power_on()


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
            and1.I[0].value = truth_table[i][0][0]
            and1.I[1].value = truth_table[i][0][1]
            and2.I[0].value = truth_table[i][0][2]
            and2.I[1].value = truth_table[i][0][3]
            and1.step()
            and2.step()
            or1.step()
            self.assertEqual(or1.O.value, truth_table[i][1])

    def test_And_connect(self):
        bf1 = Buffer('bf1')
        bf2 = Buffer('bf2')
        bf3 = Buffer('bf3')
        and1 = And('and1')

        (bf1, bf2) >> and1 >> bf3

        bf1.power_on()
        bf2.power_on()
        bf3.power_on()
        and1.power_on()

        truth_table = [
            [[0, 0], 0],
            [[0, 1], 0],
            [[1, 0], 0],
            [[1, 1], 1],
        ]

        for i in range(len(truth_table)):
            bf1.I.value = truth_table[i][0][0]
            bf2.I.value = truth_table[i][0][1]

            bf1.step()
            bf2.step()
            and1.step()
            bf3.step()

            self.assertEqual(bf3.O.value, truth_table[i][1])





if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestGate('test_And'),
        TestGate('test_And4'),
        TestGate('test_Or'),
        TestGate('test_OrN'),
        TestGate('test_Nand'),
        TestGate('test_Nor'),
        TestGate('test_Xor'),
        TestGate('test_Buffer'),
        TestGate('test_TriStateBuffer'),
        TestGate('test_Inverter'),
        TestGate('test_AndOr'),
        TestGate('test_And_connect'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)