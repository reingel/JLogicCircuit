import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Gate import Inverter
from FlipFlop import EdgeTriggeredDtypeFlipFlop
from Branch import Branch
from Util import i2bi

class Oscillator(SimulatedCircuit):
    def __init__(self, name):
        self.inv = Inverter('inv')
        self.brn = Branch('brn')
        self.update_sequence = [self.inv, self.brn]

        self.inv >> self.brn >> self.inv

        self.I = self.inv.I
        self.O = self.brn

        super().__init__('Oscillator', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {self.O.value})'
    

class RippleCounter(SimulatedCircuit):
    def __init__(self, name, nbit):
        self.device_name = 'RippleCounter'
        self.name = name
        self.nbit = nbit

        self.osc = Oscillator('osc')
        self.inv = Inverter('inv')
        self.etff = [EdgeTriggeredDtypeFlipFlop(f'etff{i}') for i in range(self.nbit - 1)]
        self.brn = [Branch(f'brn{i}') for i in range(self.nbit)]

        self.update_sequence = [self.osc, self.brn[0], self.inv]
        for i in range(self.nbit - 1):
            self.update_sequence.extend([self.etff[i], self.brn[i + 1]])

        self.osc.O >> self.brn[0] >> (self.inv, self.etff[0].Clk)
        if self.nbit > 2:
            for i in range(self.nbit - 2):
                self.etff[i].Qbar >> self.brn[i + 1] >> (self.etff[i + 1].Clk, self.etff[i].D)
        self.etff[self.nbit - 2].Qbar >> self.brn[self.nbit - 1] >> self.etff[self.nbit - 2].D

        self.Q = [self.inv.O]
        self.Q.extend([self.etff[i].Q for i in range(self.nbit - 1)])

        super().__init__(self.device_name, self.name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {self.get_output()})'
    
    def get_output(self):
        return f'{" ".join([str(self.Q[i].value) for i in range(2)][::-1])}'
    
    def init(self):
        for i in range(self.nbit - 1):
            self.etff[i].step()


class RippleCounter2Bit(RippleCounter):
    def __init__(self, name):
        super().__init__(name, 2)


class RippleCounter4Bit(RippleCounter):
    def __init__(self, name):
        super().__init__(name, 4)


class TestClock(unittest.TestCase):
    def test_oscillator(self):
        print('test_oscillator')

        osc = Oscillator('osc1')
        osc.power_on()
        osc.step()
        # print(osc.O.value, end=' ')
        self.assertEqual(osc.O.value, HIGH)
        for i in range(6):
            osc.step()
            # print(osc.O.value, end=' ')
            if i % 2 == 0:
                self.assertEqual(osc.O.value, OPEN)
            else:
                self.assertEqual(osc.O.value, HIGH)
        # print('\n')
    
    def test_ripple_counter_2bit(self):
        print('test_ripple_counter_2bit')

        rc = RippleCounter2Bit('rc')
        rc.power_on()
        rc.init()
        for i in range(10):
            rc.step()
            # print(rc.get_output())
            ans = i2bi(i % 4, 2)
            for j in range(2):
                self.assertEqual(rc.Q[j].value, int(ans[j]))

    def test_ripple_counter_4bit(self):
        print('test_ripple_counter_4bit')

        rc = RippleCounter4Bit('rc')
        rc.power_on()
        rc.init()
        for i in range(20):
            rc.step()
            # print(rc.get_output())
            ans = i2bi(i % 16, 4)
            for j in range(4):
                self.assertEqual(rc.Q[j].value, int(ans[j]))



if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests([
        TestClock('test_oscillator'),
        TestClock('test_ripple_counter_2bit'),
        TestClock('test_ripple_counter_4bit'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)