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
        else:
            raise(RuntimeError)

    def add_outport(self, port):
        if isinstance(port, Port):
            self.outports.append(port)
        else:
            raise(RuntimeError)
    
    def __lshift__(self, port):
        self.add_inport(port)
    
    def __rshift__(self, port):
        self.add_outport(port)
    
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
                    p.value = HIGH
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
            self.ri.value = OPEN
        elif (self.lu.value == HIGH and self.ld.value == OPEN) or \
            (self.lu.value == OPEN and self.ld.value == HIGH) or \
            (self.lu.value == HIGH and self.ld.value == HIGH):
            self.ri.value = HIGH
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
        dev1 = And('and1')

        p1 = Port('p1', dev1)
        p2 = Port('p2', dev1)
        p3 = Port('p3', dev1)
        q1 = Port('q1', dev1)
        q2 = Port('q2', dev1)
        q3 = Port('q3', dev1)

        brn = Branch('brn1')
        # brn.add_inport(p1)
        # brn.add_inport(p2)
        # brn.add_inport(p3)
        # brn.add_outport(q1)
        # brn.add_outport(q2)
        # brn.add_outport(q3)
        brn << p1
        brn << p2
        brn << p3
        brn >> q1
        brn >> q2
        brn >> q3

        for v1 in BITVALUES:
            for v2 in BITVALUES:
                for v3 in BITVALUES:
                    try:
                        p1.value = v1
                        p2.value = v2
                        p3.value = v3
                        print(brn)
                        brn.step()
                        print(brn)
                        print(strof(brn.value))
                        print('---')
                    except NotImplementedError:
                        print('---')

    # def test_split(self):
    #     spl = Split('spl1')
    #     print(spl)
    #     for i in [HIGH, OPEN, GND]:
    #         spl.I.value = i
    #         spl.step()
    #         print(spl)
    #         self.assertEqual(spl.I.value, i)
    #         self.assertEqual(spl.I.value, spl.O0.value)
    #         self.assertEqual(spl.I.value, spl.O1.value)
    
    # def test_merge(self):
    #     jnc = Merge('jnc1')
    #     print(jnc)
    #     jnc.I0.value = HIGH
    #     jnc.step()
    #     print(jnc)
    #     jnc.I1.value = HIGH
    #     jnc.step()
    #     print(jnc)
    #     jnc.I0.value = OPEN
    #     jnc.step()
    #     print(jnc)
    #     jnc.I1.value = OPEN
    #     jnc.step()
    #     print(jnc)
    
    # def test_split8(self):
    #     sp = Split8('split8')
    #     sp.power_on()
    #     sp.step()

    #     print(sp)
    #     sp.I.value = HIGH
    #     sp.step()
    #     print(sp)
    
if __name__ == '__main__':
    from Gate import And

    unittest.main()