import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Gate import And, Xor
from Junction import Split


class HalfAdder(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'HalfAdder'

        # creat update_sequence
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

        # update sequences
        self.update_sequence = [self.spl1, self.spl2, self.xor, self.and1]
    
        super().__init__('HalfAdder', name)

    def __repr__(self):
        str = f'   {self.device_name}({self.name}, [A B S CO] = [{self.A.value} {self.B.value} {self.S.value} {self.CO.value}]'
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
                ha.step(n=2)
                print(ha)
                self.assertEqual(ha.S.value, truth_table_S[in1][in2])
                self.assertEqual(ha.CO.value, truth_table_CO[in1][in2])



if __name__ == '__main__':
    unittest.main()
