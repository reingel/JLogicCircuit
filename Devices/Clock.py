import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Gate import Inverter
from FlipFlop import EdgeTriggeredDtypeFlipFlop
from Junction import Split

class Oscillator(SimulatedCircuit):
    def __init__(self, name):
        self.inv = Inverter('inv')
        self.spl = Split('spl')
        self.update_sequence = [self.inv, self.spl]

        self.inv.O >> self.spl.I
        self.spl.O1 >> self.inv.I

        self.I = self.inv.I
        self.O = self.spl.O0

        super().__init__('Oscillator', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {self.O.value})'
    

class RippleCounter2Bit(SimulatedCircuit):
    def __init__(self, name):
        self.osc = Oscillator('osc')
        self.inv = Inverter('inv')
        self.etff1 = EdgeTriggeredDtypeFlipFlop('etff1')
        self.spl1 = Split('spl1')
        self.spl2 = Split('spl2')

        self.update_sequence = [self.osc, self.spl1, self.inv, self.etff1, self.spl2]

        self.osc.O >> self.spl1.I
        self.spl1.O0 >> self.inv.I
        self.spl1.O1 >> self.etff1.Clk
        self.etff1.Qbar >> self.spl2.I
        self.spl2.O1 >> self.etff1.D

        self.Q = [self.inv.O, self.etff1.Q]

        super().__init__('RippleCounter2Bit', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {self.get_output()})'
    
    def get_output(self):
        return f'{" ".join([str(self.Q[i].value) for i in range(2)][::-1])}'

    def init(self):
        self.etff1.step()

class RippleCounter4Bit(SimulatedCircuit):
    def __init__(self, name):
        self.osc = Oscillator('osc')
        self.inv = Inverter('inv')
        self.etff1 = EdgeTriggeredDtypeFlipFlop('etff1')
        self.etff2 = EdgeTriggeredDtypeFlipFlop('etff2')
        self.etff3 = EdgeTriggeredDtypeFlipFlop('etff3')
        self.spl1 = Split('spl1')
        self.spl2 = Split('spl2')
        self.spl3 = Split('spl3')
        self.spl4 = Split('spl4')

        self.update_sequence = [self.osc, self.spl1, self.inv, self.etff1, self.spl2, self.etff2, self.spl3, self.etff3, self.spl4]

        self.osc.O >> self.spl1.I
        self.spl1.O0 >> self.inv.I
        self.spl1.O1 >> self.etff1.Clk
        self.etff1.Qbar >> self.spl2.I
        self.spl2.O0 >> self.etff2.Clk
        self.spl2.O1 >> self.etff1.D
        self.etff2.Qbar >> self.spl3.I
        self.spl3.O0 >> self.etff3.Clk
        self.spl3.O1 >> self.etff2.D
        self.etff3.Qbar >> self.spl4.I
        self.spl4.O1 >> self.etff3.D

        self.Q = [self.inv.O, self.etff1.Q, self.etff2.Q, self.etff3.Q]

        super().__init__('RippleCounter4Bit', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {self.get_output()})'
    
    def get_output(self):
        return f'{" ".join([str(self.Q[i].value) for i in range(4)][::-1])}'

    def init(self):
        self.etff1.step()
        self.etff2.step()
        self.etff3.step()


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
            ans = f'{i % 4:02b}'[::-1]
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
            ans = f'{i % 16:04b}'[::-1]
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