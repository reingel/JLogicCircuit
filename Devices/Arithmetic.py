import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Gate import And, Or, Xor
from Branch import Branch
from Source import Ground
from Util import i2bi


class HalfAdder(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'HalfAdder'
        self.name = name

        # create elements
        self.brn1 = Branch('brn1')
        self.brn2 = Branch('brn2')
        self.xor = Xor('xor')
        self.and1 = And('and1')

        # connect
        self.brn1 >> (self.xor.I[0], self.and1.I[0])
        self.brn2 >> (self.xor.I[1], self.and1.I[1])

        # create access points
        self.A = self.brn1
        self.B = self.brn2
        self.S = self.xor.O
        self.CO = self.and1.O

        # update sequence
        self.update_sequence = [self.brn1, self.brn2, self.xor, self.and1]
    
        super().__init__(self.device_name, self.name)

    def __repr__(self):
        str = f'{self.device_name}({self.name}, [A B] -> [S CO] = [{self.A.value} {self.B.value}] -> [{self.S.value} {self.CO.value}]'
        return str


class FullAdder(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'FullAdder'
        self.name = name

        # create elements
        self.ha1 = HalfAdder('ha1')
        self.ha2 = HalfAdder('ha2')
        self.or1 = Or('or1')

        # connect
        self.ha1.S >> self.ha2.B
        self.ha2.CO >> self.or1.I[0]
        self.ha1.CO >> self.or1.I[1]

        # create access points
        self.CI = self.ha2.A
        self.A = self.ha1.A
        self.B = self.ha1.B
        self.S = self.ha2.S
        self.CO = self.or1.O

        # update sequence
        self.update_sequence = [self.ha1, self.ha2, self.or1]

        super().__init__(self.device_name, self.name)

    def __repr__(self):
        str = f'{self.device_name}({self.name}, [CI A B] -> [S CO] = [{self.CI.value} {self.A.value} {self.B.value}] -> [{self.S.value} {self.CO.value}]'
        return str


class Adder8bit(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'Adder8bit'
        self.num_adder = 8

        # create elements
        self.fa = [FullAdder(f'fa{i}') for i in range(self.num_adder)]

        # connect
        for i in range(self.num_adder - 1):
            self.fa[i].CO >> self.fa[i + 1].CI

        # create access points
        self.CI = self.fa[0].CI
        self.A = [self.fa[i].A for i in range(self.num_adder)]
        self.B = [self.fa[i].B for i in range(self.num_adder)]
        self.S = [self.fa[i].S for i in range(self.num_adder)]
        self.CO = self.fa[self.num_adder-1].CO

        # update sequence
        self.update_sequence = [self.fa[i] for i in range(self.num_adder)]

        super().__init__(self.device_name, name)

    def __repr__(self):
        strA = ''
        strB = ''
        strS = ''
        for i in range(self.num_adder):
            strA = f'{self.A[i].value}{strA}'
            strB = f'{self.B[i].value}{strB}'
            strS = f'{self.S[i].value}{strS}'
        str = f'{self.device_name}({self.name})\n  A = {strA}\n+ B = {strB}\n----------------\n  S = {strS}\n CO = {self.CO.value}'
        return str
    
    def set_input(self, A: int, B: int):
        if A > 255 or A < 0 or B > 255 or B < 0:
            raise(RuntimeError)
        strA = i2bi(A, 8)
        strB = i2bi(B, 8)
        for i in range(self.num_adder):
            self.A[i].value = int(strA[i])
            self.B[i].value = int(strB[i])
    
    def get_output(self):
        strS = ''
        for i in range(self.num_adder):
            strS = f'{self.S[i].value}{strS}'
        S = int(strS, 2)
        return S


class TestArithmetic(unittest.TestCase):
    def test_half_adder(self):
        print('test_half_adder')

        ha = HalfAdder('ha1')
        ha.power_on()
        ha.step()
        truth_table_S = [[OPEN, HIGH], [HIGH, OPEN]]
        truth_table_CO = [[OPEN, OPEN], [OPEN, HIGH]]
        for v0 in [OPEN, HIGH]:
            for v1 in [OPEN, HIGH]:
                ha.A.value = v0
                ha.B.value = v1
                ha.step()
                # print(ha)
                self.assertEqual(ha.S.value, truth_table_S[v0][v1])
                self.assertEqual(ha.CO.value, truth_table_CO[v0][v1])

    def test_full_adder(self):
        print('test_full_adder')

        fa = FullAdder('fa1')
        fa.power_on()
        fa.step()
        truth_table_S = [[[0, 1], [1, 0]], [[1, 0], [0, 1]]]
        truth_table_CO = [[[0, 0], [0, 1]], [[0, 1], [1, 1]]]
        for ci in [OPEN, HIGH]:
            for v0 in [OPEN, HIGH]:
                for v1 in [OPEN, HIGH]:
                    fa.CI.value = ci
                    fa.A.value = v0
                    fa.B.value = v1
                    fa.step()
                    # print(fa)
                    self.assertEqual(fa.S.value, truth_table_S[ci][v0][v1])
                    self.assertEqual(fa.CO.value, truth_table_CO[ci][v0][v1])

    def test_adder8bit(self):
        print('test_adder8bit')

        gnd = Ground('gnd')
        a8 = Adder8bit('a8')
        gnd.O >> a8.CI
        gnd.power_on()
        a8.power_on()
        gnd.step()
        a8.step()

        A = 19
        B = 115
        a8.set_input(A, B)
        a8.step()
        S = a8.get_output()
        # print(f'{A} + {B} = {S}')
        self.assertEqual(S, (A + B) % 256)
        self.assertEqual(a8.CO.value, 1 if (A + B) >= 256 else 0)
        # print(a8)

        A = 198
        B = 115
        a8.set_input(A, B)
        a8.step()
        S = a8.get_output()
        # print(f'{A} + {B} = {S}')
        self.assertEqual(S, (A + B) % 256)
        self.assertEqual(a8.CO.value, 1 if (A + B) >= 256 else 0)
        # print(a8)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestArithmetic('test_half_adder'),
        TestArithmetic('test_full_adder'),
        TestArithmetic('test_adder8bit'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)