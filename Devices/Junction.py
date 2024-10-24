import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port


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
        return f'Split({self.name}, {self.I.value} -> {self.O0.value} + {self.O1.value})'
    
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
        return f'Merge({self.name}, {self.I0.value} + {self.I1.value} -> {self.O.value})'
    
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
        return f'Split({self.name}, {self.I.value} -> {[self.O[i].value for i in range(self.n)]})'
    
    def update_inport(self):
        self.I.update_value()
    
    def calc_output(self):
        for i in range(self.n):
            self.O[i].value = self.I.value
    
    def update_state(self):
        pass # there is no state.



class TestConnection(unittest.TestCase):
    def test_split(self):
        spl = Split('spl1')
        print(spl)
        spl.I.value = HIGH
        spl.step()
        print(spl)
        self.assertEqual(spl.I.value, HIGH)
        self.assertEqual(spl.I.value, spl.O0.value)
        self.assertEqual(spl.I.value, spl.O1.value)
        spl.I.value = OPEN
        spl.step()
        print(spl)
        self.assertEqual(spl.I.value, OPEN)
        self.assertEqual(spl.I.value, spl.O0.value)
        self.assertEqual(spl.I.value, spl.O1.value)
    
    def test_merge(self):
        jnc = Merge('jnc1')
        print(jnc)
        jnc.I0.value = HIGH
        jnc.step()
        print(jnc)
        jnc.I1.value = HIGH
        jnc.step()
        print(jnc)
        jnc.I0.value = OPEN
        jnc.step()
        print(jnc)
        jnc.I1.value = OPEN
        jnc.step()
        print(jnc)
    
    def test_split8(self):
        sp = Split8('split8')
        sp.power_on()
        sp.step()

        print(sp)
        sp.I.value = HIGH
        sp.step()
        print(sp)
    
if __name__ == '__main__':
    unittest.main()