import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Gate import Inverter, And, OrN
from Branch import Branch
from Arithmetic import Adder8bit
from Counter import Oscillator, RippleCounter4Bit
from FlipFlop import EdgeTriggeredDtypeFlipFlop, Latch8bit
from Memory import RAM256x8
from Util import i2bi


class ControlSignal(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'ControlSignal'
        self.name = name
        self.nff = 2

        self.osc = Oscillator('osc')
        self.brnc = Branch('brnc')
        self.brnd = Branch('brnd')
        self.brnqb = Branch('brnqb')
        self.inv = Inverter('inv')
        self.ff = [EdgeTriggeredDtypeFlipFlop(f'ff{i}') for i in range(self.nff)]
        self.andp = And('andp')
        self.brnp = Branch('brnp')
        self.or8 = OrN('or8', 8)
        self.invor = Inverter('invor') # TODO: to be combined with or8
        self.andw = And('andw')

        self.osc.O >> self.brnc >> (self.inv, self.ff[0].Clk)
        self.inv >> self.ff[1].Clk
        self.ff[0].Q >> self.brnd >> self.ff[1].D
        self.ff[0].Qbar >> self.brnqb >> (self.ff[0].D, self.andp.I[0])
        self.ff[1].Q >> self.andp.I[1]
        self.andp.O >> self.brnp >> self.andw.I[0]
        self.or8.O >> self.invor >> self.andw.I[1]

        self.DI = self.or8.I
        self.ToCounterClk = self.brnd
        self.ToLatchClk = self.brnp
        self.ToRamW = self.andw.O

        self.update_sequence = [self.osc, self.inv]
        self.update_sequence.extend([self.ff[i] for i in range(self.nff)])
        self.update_sequence.append(self.andp)
        self.update_sequence.append(self.or8)
        self.update_sequence.append(self.andw)

        super().__init__(self.device_name, self.name)


class AutomatedAccumulatedAdder(SimulatedCircuit):
    def __init__(self, name):
        self.device_name = 'AutomatedAccumulatedAdder'
        self.name = name
        self.naddr = 4
        self.nbit = 8

        self.cs = ControlSignal('cs')
        self.counter = RippleCounter4Bit('counter')
        self.ram = RAM256x8('ram')
        self.adder = Adder8bit('adder')
        self.latch = Latch8bit('latch')
        self.brndi = [Branch(f'brndi{i}') for i in range(self.nbit)]
        self.brndo = [Branch(f'brnramdo{i}') for i in range(self.nbit)]

        for i in range(self.naddr):
            self.counter.Q[i] >> self.ram.A[i]
        for i in range(self.nbit):
            self.ram.DO[i] >> self.brndo >> (self.adder.A[i], self.cs.DI[i])
            self.adder.S[i] >> self.latch.D[i]
            self.latch.Q[i] >> self.brndi[i] >> (self.ram.DI[i], self.adder.B[i])
        self.cs.ToCounterClk >> self.counter.Clk
        self.cs.ToLatchClk >> self.latch.Clk
        self.cs.ToRamW >> self.ram.W
        
        self.ram.E.set()
        self.update_sequence = [self.counter, self.ram, self.adder, self.latch, self.ram]

        super().__init__(self.device_name, self.name)
    


