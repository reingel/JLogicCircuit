import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from Gate import Inverter
from FlipFlop import EdgeTriggeredDtypeFlipFlip
from Junction import Split

class Oscillator(SimulatedCircuit):
    def __init__(self, name):
        self.inv = Inverter('inv')
        self.spl = Split('spl')
        self.update_sequence = [self.inv, self.spl]

        self.inv.out >> self.spl.in1
        self.spl.out2 >> self.inv.in1

        self.in1 = self.inv.in1
        self.out = self.spl.out1

        super().__init__('Oscillator', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, {self.out.value})'
    

class RippleCounter2Bit(SimulatedCircuit):
    def __init__(self, name):
        self.osc = Oscillator('osc')
        self.inv = Inverter('inv')
        self.etff1 = EdgeTriggeredDtypeFlipFlip('etff1')
        self.spl1 = Split('spl1')
        self.spl2 = Split('spl2')

        self.update_sequence = [self.osc, self.spl1, self.inv, self.etff1, self.spl2]

        self.osc.out >> self.spl1.in1
        self.spl1.out1 >> self.inv.in1
        self.spl1.out2 >> self.etff1.Clk
        self.etff1.Qbar >> self.spl2.in1
        self.spl2.out2 >> self.etff1.D

        self.Clkbar = self.inv.out
        self.Q1 = self.etff1.Q

        super().__init__('RippleCounter2Bit', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, [{self.Q1.value} {self.Clkbar.value}])'

    def init(self):
        self.etff1.step()

class RippleCounter4Bit(SimulatedCircuit):
    def __init__(self, name):
        self.osc = Oscillator('osc')
        self.inv = Inverter('inv')
        self.etff1 = EdgeTriggeredDtypeFlipFlip('etff1')
        self.etff2 = EdgeTriggeredDtypeFlipFlip('etff2')
        self.etff3 = EdgeTriggeredDtypeFlipFlip('etff3')
        self.spl1 = Split('spl1')
        self.spl2 = Split('spl2')
        self.spl3 = Split('spl3')
        self.spl4 = Split('spl4')

        self.update_sequence = [self.osc, self.spl1, self.inv, self.etff1, self.spl2, self.etff2, self.spl3, self.etff3, self.spl4]

        self.osc.out >> self.spl1.in1
        self.spl1.out1 >> self.inv.in1
        self.spl1.out2 >> self.etff1.Clk
        self.etff1.Qbar >> self.spl2.in1
        self.spl2.out1 >> self.etff2.Clk
        self.spl2.out2 >> self.etff1.D
        self.etff2.Qbar >> self.spl3.in1
        self.spl3.out1 >> self.etff3.Clk
        self.spl3.out2 >> self.etff2.D
        self.etff3.Qbar >> self.spl4.in1
        self.spl4.out2 >> self.etff3.D

        self.Clkbar = self.inv.out
        self.Q1 = self.etff1.Q
        self.Q2 = self.etff2.Q
        self.Q3 = self.etff3.Q

        super().__init__('RippleCounter4Bit', name)
    
    def __repr__(self):
        return f'{self.device_name}({self.name}, [{self.Q3.value} {self.Q2.value} {self.Q1.value} {self.Clkbar.value}])'
    
    def init(self):
        self.etff1.step()
        self.etff2.step()
        self.etff3.step()


class TestClock(unittest.TestCase):
    # def test_oscillator(self):
    #     osc = Oscillator('osc1')
    #     osc.power_on()
    #     osc.step()
    #     print(osc)
    #     for i in range(6):
    #         osc.step(n=1)
    #         print(osc)
    
    def test_ripple_counter_2bit(self):
        rc = RippleCounter2Bit('rc')
        rc.power_on()
        rc.init()
        for i in range(10):
            rc.step(n=1)
            print(rc)
            a=1

    def test_ripple_counter_4bit(self):
        rc = RippleCounter4Bit('rc')
        rc.power_on()
        rc.init()
        for i in range(20):
            rc.step(n=1)
            print(rc)
            a=1



if __name__ == '__main__':
    unittest.main()