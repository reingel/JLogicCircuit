import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Gate import And, Or, Xor
from Junction import Split


class HalfAdder(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'HalfAdder'

        # create elements
        self.spl1 = Split('spl1')
        self.spl2 = Split('spl2')
        self.xor = Xor('xor')
        self.and1 = And('and1')

        # connect
        self.spl1.out1 >> self.xor.in1
        self.spl1.out2 >> self.and1.in1
        self.spl2.out1 >> self.xor.in2
        self.spl2.out2 >> self.and1.in2

        # create access points
        self.A = self.spl1.in1
        self.B = self.spl2.in1
        self.S = self.xor.out
        self.CO = self.and1.out

        # update sequence
        self.update_sequence = [self.spl1, self.spl2, self.xor, self.and1]
    
        super().__init__('HalfAdder', name)

    def __repr__(self):
        str = f'   {self.device_name}({self.name}, [A B] -> [S CO] = [{self.A.value} {self.B.value}] -> [{self.S.value} {self.CO.value}]'
        # str += '\n'
        # for device in self.update_sequence:
        #     str += f'      {device}\n'
        return str


class FullAdder(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'FullAdder'

        # create elements
        self.ha1 = HalfAdder('ha1')
        self.ha2 = HalfAdder('ha2')
        self.or1 = Or('or1')

        # connect
        self.ha1.S >> self.ha2.B
        self.ha2.CO >> self.or1.in1
        self.ha1.CO >> self.or1.in2

        # create access points
        self.CI = self.ha2.A
        self.A = self.ha1.A
        self.B = self.ha1.B
        self.S = self.ha2.S
        self.CO = self.or1.out

        # update sequence
        self.update_sequence = [self.ha1, self.ha2, self.or1]

        super().__init__('FullAdder', name)

    def __repr__(self):
        str = f'   {self.device_name}({self.name}, [CI A B] -> [S CO] = [{self.CI.value} {self.A.value} {self.B.value}] -> [{self.S.value} {self.CO.value}]'
        # str += '\n'
        # for device in self.update_sequence:
        #     str += f'      {device}\n'
        return str


class TestArithmetic(unittest.TestCase):
    def test_half_adder(self):
        ha = HalfAdder('ha1')
        ha.power_on()
        ha.step()
        truth_table_S = [[OPEN, HIGH], [HIGH, OPEN]]
        truth_table_CO = [[OPEN, OPEN], [OPEN, HIGH]]
        for in1 in [OPEN, HIGH]:
            for in2 in [OPEN, HIGH]:
                ha.A.value = in1
                ha.B.value = in2
                ha.step()
                print(ha)
                self.assertEqual(ha.S.value, truth_table_S[in1][in2])
                self.assertEqual(ha.CO.value, truth_table_CO[in1][in2])

    def test_full_adder(self):
        fa = FullAdder('fa1')
        fa.power_on()
        fa.step()
        truth_table_S = [[[0, 1], [1, 0]], [[1, 0], [0, 1]]]
        truth_table_CO = [[[0, 0], [0, 1]], [[0, 1], [1, 1]]]
        for ci in [OPEN, HIGH]:
            for in1 in [OPEN, HIGH]:
                for in2 in [OPEN, HIGH]:
                    fa.CI.value = ci
                    fa.A.value = in1
                    fa.B.value = in2
                    fa.step()
                    print(fa)
                    self.assertEqual(fa.S.value, truth_table_S[ci][in1][in2])
                    self.assertEqual(fa.CO.value, truth_table_CO[ci][in1][in2])


if __name__ == '__main__':
    unittest.main()
