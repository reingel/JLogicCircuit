import unittest
import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Constant import *
from Util import *
from Device import Device
from Power import Power
from Ground import Ground
from Relay import Relay
from Switch import Switch
from GateNor import GateNor

class GateRSFlipFlop(Device):
    def __init__(self, name):
        # U: input vector, X: state vector, Y: output vector
        self.nU = 2
        self.nY = 1

        self.nor1 = GateNor('nor1')
        self.nor2 = GateNor('nor2')

        self.nor1.out.connect(self.nor2.in1)
        self.nor2.out.connect(self.nor1.in2)

        self.R = self.nor1.in1
        self.S = self.nor2.in2
        self.Q = self.nor1.out
        self.Qbar = self.nor2.out

        super().__init__(name)
    
    def __repr__(self):
        ports = bool2int(np.array([self.R, self.S, self.Q, self.Qbar]))
        return f'GateRSFlipFlop({self.name}, [R S Q Qbar] = {ports}'

    def set_input(self, r: bool, s: bool):
        self.R.set_volt(r)
        self.S.set_volt(s)
    
    def get_output(self):
        return np.array([self.Q.volt, self.Qbar.volt])
    
    def calc_output(self):
        self.nor1.in1.update()
        self.nor1.in2.update()
        self.nor2.in1.update()
        self.nor2.in2.update()
        self.nor1.calc_output()
        self.nor2.calc_output()
        
    def update(self):
        self.nor1.update()
        self.nor2.update()


class TestGateRSFlipFlop(unittest.TestCase):
    def test_FF(self):
        gate = GateRSFlipFlop('gate1')
        gate.set_input(LOW, LOW)
        gate.calc_output()
        gate.update()
        gate.set_input(HIGH, LOW)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), np.array([LOW, HIGH]))
        print(gate)
        gate.update()

    def test_TF(self):
        gate = GateRSFlipFlop('gate2')
        gate.set_input(HIGH, LOW)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), HIGH)
        print(gate)
        gate.update()

    def test_FT(self):
        gate = GateRSFlipFlop('gate3')
        gate.set_input(LOW, HIGH)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), HIGH)
        print(gate)
        gate.update()

    def test_TT(self):
        gate = GateRSFlipFlop('gate4')
        gate.set_input(HIGH, HIGH)
        gate.calc_output()
        gate.update()
        gate.calc_output()
        self.assertEqual(gate.get_output(), LOW)
        print(gate)
        gate.update()



if __name__ == '__main__':
    unittest.main()