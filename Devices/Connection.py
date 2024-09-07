import unittest
from EStatus import *
from Device import Device
from Port import Port


class Connection:
    def __init__(self):
        pass
    
    def step(self, n=1):
        for i in range(n):
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
        return f'Split({self.in1.status} -> {self.out1.status} + {self.out2.status})'
    
    def calc_output(self):
        self.le.update_status()
        self.ru.status = self.le.status
        self.rd.status = self.le.status
    
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
        return f'Junction({self.in1.status} + {self.in2.status} -> {self.out.status})'
    
    def calc_output(self):
        self.lu.update_status()
        self.ld.update_status()
        if self.lu.status == OPEN and self.ld.status == OPEN:
            self.ri.status = OPEN
        elif (self.lu.status == HIGH and self.ld.status == OPEN) or \
            (self.lu.status == OPEN and self.ld.status == HIGH) or \
            (self.lu.status == HIGH and self.ld.status == HIGH):
            self.ri.status = HIGH
        else:
            raise(RuntimeError)
    
    def update_state(self):
        pass # there is no state.


class TestConnection(unittest.TestCase):
    def test_split(self):
        spl = Split('spl1')
        print(spl)
        spl.in1.status = HIGH
        spl.step()
        print(spl)
        spl.in1.status = OPEN
        spl.step()
        print(spl)

    
    def test_junction(self):
        jnc = Junction('jnc1')
        print(jnc)
        jnc.in1.status = HIGH
        jnc.step()
        print(jnc)
        jnc.in2.status = HIGH
        jnc.step()
        print(jnc)
        jnc.in1.status = OPEN
        jnc.step()
        print(jnc)
        jnc.in2.status = OPEN
        jnc.step()
        print(jnc)

if __name__ == '__main__':
    unittest.main()