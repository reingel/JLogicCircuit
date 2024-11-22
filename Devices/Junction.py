import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port


class Branch(SimulatedCircuit):
    '''
    I: list of input ports
    O: list of output ports
    state: state(HIGH, OPEN, or GND) of Branch
    '''
    def __init__(self, name):
        self.device_name = 'Branch'
        self.name = name

        self._state = OPEN
        self._nI = 0
        self._nO = 0

        self.I = []
        self.O = []

        super().__init__(self.device_name, self.name)
    
    def __repr__(self):
        return f'Branch({self.name}, {[strof(p.value) for p in self.I]} -> {strof(self.state)} -> {[strof(p.value) for p in self.O]})'
    
    @property
    def state(self):
        return self._state
    
    @property
    def nI(self):
        return self._nI
    
    @property
    def nO(self):
        return self._nO
    
    @property
    def is_not_empty(self):
        return self.nI > 0 and self.nO > 0

    def add_inport(self, port):
        if isinstance(port, Port):
            n = self.nI
            p = Port(f'I{n + 1}', self)
            port >> p
            self.I.append(p)
            self._nI += 1
            return self
        else:
            raise(RuntimeError)

    def add_outport(self, port):
        if isinstance(port, Port):
            n = self.nO
            p = Port(f'O{n + 1}', self)
            p >> port
            self.O.append(p)
            self._nO += 1
        else:
            raise(RuntimeError)
    
    def __lshift__(self, port):
        return self.add_inport(port)

    def __rshift__(self, port):
        self.add_outport(port)
    
    def __rrshift__(self, port):
        return self.__lshift__(port)
    
    def update_inport(self):
        for p in self.I:
            p.update_value()

    def update_state(self):
        if self.nI == 0:
            return

        values = set([p.value for p in self.I])
        if HIGH in values and GND in values:
            # print('Short circuit !!!')
            raise(NotImplementedError)
        elif HIGH in values:
            self._state = HIGH
        elif GND in values:
            self._state = GND
        else:
            self._state = OPEN

        for p in self.I:
            p.value = self.state

    def calc_output(self):
        for p in self.O:
            p.value = self.state


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
        self.assertEqual(brn.is_not_empty, False)
        p1 >> brn >> q1
        p2 >> brn >> q2
        p3 >> brn >> q3
        self.assertEqual(brn.nI, 3)
        self.assertEqual(brn.nO, 3)
        self.assertEqual(brn.is_not_empty, True)

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
                q1.update_value()
                q2.update_value()
                q3.update_value()
                # print(brn, q1, q2, q3)
                self.assertEqual(brn.state, io[i][1])
                self.assertEqual(q1.value, brn.state)
                self.assertEqual(q2.value, brn.state)
                self.assertEqual(q3.value, brn.state)
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