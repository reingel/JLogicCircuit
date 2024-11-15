import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port


class Branch(SimulatedCircuit):
    def __init__(self, name):
        self.name = name
        self.inports = []
        self.outports = []

        super().__init__('Branch', self.name)
    
    def __repr__(self):
        return f'Branch({self.name}, in = {[strof(p.value) for p in self.inports]}, out = {[strof(p.value) for p in self.outports]})'
    
    @property
    def ninport(self):
        return len(self.inports)
    
    @property
    def noutport(self):
        return len(self.outports)
    
    @property
    def exists(self):
        return self.ninport > 0 and self.noutport > 0
    
    @property
    def value(self):
        if self.ninport > 0:
            return self.inports[0].value
        else:
            return None

    def add_inport(self, port):
        if isinstance(port, Port):
            self.inports.append(port)
            return self
        else:
            raise(RuntimeError)

    def add_outport(self, port):
        if isinstance(port, Port):
            self.outports.append(port)
        else:
            raise(RuntimeError)
    
    def __lshift__(self, port):
        return self.add_inport(port)

    def __rshift__(self, port):
        self.add_outport(port)
    
    def __rrshift__(self, port):
        return self.__lshift__(port)
    
    def update_inport(self):
        if self.ninport == 0:
            return

        values = set([p.value for p in self.inports])
        if HIGH in values and GND in values:
            print('Short circuit !!!')
            raise(NotImplementedError)
        elif HIGH in values and GND not in values:
            for p in self.inports:
                if p.value == OPEN:
                    p.set()
        elif GND in values and HIGH not in values:
            for p in self.inports:
                if p.value == OPEN:
                    p.value = GND

    def calc_output(self):
        if not self.exists:
            return
        
        for p in self.outports:
            p.value = self.value

    def update_state(self):
        pass

class Junction(SimulatedCircuit):
    def __init__(self):
        pass
    

class Split(Junction):
    def __init__(self, name):
        self.name = name

        # create ports
        self.le = Port('le', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        # create access points
        self.I = self.le
        self.O0 = self.ru
        self.O1 = self.rd

        super().__init__()

    def __repr__(self):
        return f'Split({self.name}, {strof(self.I.value)} -> {strof(self.O0.value)} + {strof(self.O1.value)})'
    
    def update_inport(self):
        self.le.update_value()
    
    def calc_output(self):
        self.ru.value = self.le.value
        self.rd.value = self.le.value
    
    def update_state(self):
        pass # there is no state.


class Merge(Junction):
    def __init__(self, name):
        self.name = name

        # create ports
        self.lu = Port('lu', self)
        self.ld = Port('ld', self)
        self.ri = Port('ri', self)

        # create access points
        self.I0 = self.lu
        self.I1 = self.ld
        self.O = self.ri

        super().__init__()
    
    def __repr__(self):
        return f'Merge({self.name}, {strof(self.I0.value)} + {strof(self.I1.value)} -> {strof(self.O.value)})'
    
    def update_inport(self):
        self.lu.update_value()
        self.ld.update_value()
    
    def calc_output(self):
        if self.lu.value == OPEN and self.ld.value == OPEN:
            self.ri.reset()
        elif (self.lu.value == HIGH and self.ld.value == OPEN) or \
            (self.lu.value == OPEN and self.ld.value == HIGH) or \
            (self.lu.value == HIGH and self.ld.value == HIGH):
            self.ri.set()
        else:
            raise(RuntimeError)
    
    def update_state(self):
        pass # there is no state.

class Split8(Junction):
    def __init__(self, name):
        self.name = name

        self.n = 8

        # create ports
        self.I = Port('I', self)
        self.O = [Port(f'O{i}', self) for i in range(self.n)]

        super().__init__()

    def __repr__(self):
        return f'Split({self.name}, {strof(self.I.value)} -> {[strof(self.O[i].value) for i in range(self.n)]})'
    
    def update_inport(self):
        self.I.update_value()
    
    def calc_output(self):
        for i in range(self.n):
            self.O[i].value = self.I.value
    
    def update_state(self):
        pass # there is no state.



class TestConnection(unittest.TestCase):
    def test_branch(self):
        print('test_branch')

        dev1 = And('and1')

        p1 = Port('p1', dev1)
        p2 = Port('p2', dev1)
        p3 = Port('p3', dev1)
        q1 = Port('q1', dev1)
        q2 = Port('q2', dev1)
        q3 = Port('q3', dev1)

        brn = Branch('brn1')
        p1 >> brn >> q1
        p2 >> brn >> q2
        p3 >> brn >> q3

        SHORT_CIRCUIT = 99
        io = [
            [[HIGH, HIGH, HIGH], HIGH],
            [[HIGH, HIGH, OPEN], HIGH],
            [[HIGH, HIGH, GND], SHORT_CIRCUIT],
            [[HIGH, OPEN, HIGH], HIGH],
            [[HIGH, OPEN, OPEN], HIGH],
            [[HIGH, OPEN, GND], SHORT_CIRCUIT],
            [[HIGH, GND, HIGH], SHORT_CIRCUIT],
            [[HIGH, GND, OPEN], SHORT_CIRCUIT],
            [[HIGH, GND, GND], SHORT_CIRCUIT],

            [[OPEN, HIGH, HIGH], HIGH],
            [[OPEN, HIGH, OPEN], HIGH],
            [[OPEN, HIGH, GND], SHORT_CIRCUIT],
            [[OPEN, OPEN, HIGH], HIGH],
            [[OPEN, OPEN, OPEN], OPEN],
            [[OPEN, OPEN, GND], GND],
            [[OPEN, GND, HIGH], SHORT_CIRCUIT],
            [[OPEN, GND, OPEN], GND],
            [[OPEN, GND, GND], GND],

            [[GND, HIGH, HIGH], SHORT_CIRCUIT],
            [[GND, HIGH, OPEN], SHORT_CIRCUIT],
            [[GND, HIGH, GND], SHORT_CIRCUIT],
            [[GND, OPEN, HIGH], SHORT_CIRCUIT],
            [[GND, OPEN, OPEN], GND],
            [[GND, OPEN, GND], GND],
            [[GND, GND, HIGH], SHORT_CIRCUIT],
            [[GND, GND, OPEN], GND],
            [[GND, GND, GND], GND],
        ]

        for i in range(len(io)):
            p1.value = io[i][0][0]
            p2.value = io[i][0][1]
            p3.value = io[i][0][2]
            try:
                brn.step()
                self.assertEqual(brn.value, io[i][1])
                self.assertEqual(q1.value, brn.value)
                self.assertEqual(q2.value, brn.value)
                self.assertEqual(q3.value, brn.value)
            except NotImplementedError:
                self.assertEqual(io[i][1], SHORT_CIRCUIT)


    def test_split(self):
        print('test_split')

        spl = Split('spl1')

        for v in [HIGH, OPEN, GND]:
            spl.I.value = v
            spl.step()
            self.assertEqual(spl.I.value, v)
            self.assertEqual(spl.I.value, spl.O0.value)
            self.assertEqual(spl.I.value, spl.O1.value)
    

    def test_merge(self):
        print('test_merge')

        jnc = Merge('jnc1')

        io = [
            [[HIGH, HIGH], HIGH],
            [[HIGH, OPEN], HIGH],
            [[OPEN, HIGH], HIGH],
            [[OPEN, OPEN], OPEN],
        ]

        for i in range(len(io)):
            jnc.I0.value = io[i][0][0]
            jnc.I1.value = io[i][0][1]
            jnc.step()
            self.assertEqual(jnc.O.value, io[i][1])


    def test_split8(self):
        print('test_split8')

        sp = Split8('split8')
        sp.power_on()
        sp.step()

        sp.I.set()
        sp.step()
        for i in range(8):
            self.assertEqual(sp.O[i].value, HIGH)
        
        sp.I.reset()
        sp.step()
        for i in range(8):
            self.assertEqual(sp.O[i].value, OPEN)
    
if __name__ == '__main__':
    from Gate import And

    unittest.main()