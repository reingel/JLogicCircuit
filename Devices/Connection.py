import unittest
from BitValue import *
from Device import Device
from Port import Port


class Connection:
    def __init__(self):
        pass
    
    def step(self, n=1):
        for i in range(n):
            self.update_inports()
            self.calc_output()
            self.update_state()


class Split(Connection):
    def __init__(self, name):
        self.name = name

        # create ports
        self.le = Port('le', self)
        self.ru = Port('ru', self)
        self.rd = Port('rd', self)

        # create access points
        self.in1 = self.le
        self.out1 = self.ru
        self.out2 = self.rd

        super().__init__()

    def __repr__(self):
        return f'Split({self.name}, {self.in1.value} -> {self.out1.value} + {self.out2.value})'
    
    def update_inports(self):
        self.le.update_value()
    
    def calc_output(self):
        self.ru.value = self.le.value
        self.rd.value = self.le.value
    
    def update_state(self):
        pass # there is no state.


class Junction(Connection):
    def __init__(self, name):
        self.name = name

        # create ports
        self.lu = Port('lu', self)
        self.ld = Port('ld', self)
        self.ri = Port('ri', self)

        # create access points
        self.in1 = self.lu
        self.in2 = self.ld
        self.out = self.ri

        super().__init__()
    
    def __repr__(self):
        return f'Junction({self.name}, {self.in1.value} + {self.in2.value} -> {self.out.value})'
    
    def update_inports(self):
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


class TestConnection(unittest.TestCase):
    def test_split(self):
        spl = Split('spl1')
        print(spl)
        spl.in1.value = HIGH
        spl.step()
        print(spl)
        spl.in1.value = OPEN
        spl.step()
        print(spl)

    
    def test_junction(self):
        jnc = Junction('jnc1')
        print(jnc)
        jnc.in1.value = HIGH
        jnc.step()
        print(jnc)
        jnc.in2.value = HIGH
        jnc.step()
        print(jnc)
        jnc.in1.value = OPEN
        jnc.step()
        print(jnc)
        jnc.in2.value = OPEN
        jnc.step()
        print(jnc)

if __name__ == '__main__':
    unittest.main()