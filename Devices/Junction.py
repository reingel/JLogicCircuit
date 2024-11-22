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

        self._value = OPEN
        self._ninport = 0
        self._noutport = 0

        self.inport = []
        self.outport = []

        super().__init__(self.device_name, self.name)
    
    def __repr__(self):
        return f'Branch({self.name}, {[strof(p.value) for p in self.inport]} -> {strof(self.value)} -> {[strof(p.value) for p in self.outport]})'
    
    @property
    def ninport(self):
        return self._ninport
    
    @property
    def noutport(self):
        return self._noutport
    
    @property
    def act_like_inport(self):
        return self._ninport == 0
    
    @property
    def act_like_outport(self):
        return self._noutport == 0
    
    @property
    def value(self): # In case of self.inport is empty, self acts like Port
        return self._value
    
    @value.setter
    def value(self, val): # In case of self.inport is empty, self acts like Port
        if self.act_like_inport:
            self._value = val
        else:
            raise(RuntimeError)
    
    def set(self): # In case of self.inport is empty, self acts like Port
        self.value = HIGH
    
    def reset(self): # In case of self.inport is empty, self acts like Port
        self.value = OPEN
    
    def update_value(self): # In case of self.inport is empty, self acts like Port
        pass
    
    def add_inport(self, port):
        if isinstance(port, Port) or isinstance(port, Branch):
            n = self.ninport
            p = Port(f'inport{n + 1}', self)
            port >> p
            self.inport.append(p)
            self._ninport += 1
            return self
        else:
            raise(RuntimeError)

    def add_outport(self, port):
        if isinstance(port, Port) or isinstance(port, Branch):
            n = self.noutport
            p = Port(f'outport{n + 1}', self)
            p >> port
            self.outport.append(p)
            self._noutport += 1
        else:
            raise(RuntimeError)
    
    def __lshift__(self, port):
        return self.add_inport(port)

    def __rshift__(self, port):
        self.add_outport(port)
    
    def __rrshift__(self, port):
        return self.__lshift__(port)
    
    def update_inport(self):
        for p in self.inport:
            p.update_value()

    def update_state(self):
        values = set([p.value for p in self.inport])
        if len(values) == 0:
            return

        if HIGH in values and GND in values:
            # print('Short circuit !!!')
            raise(NotImplementedError)
        elif HIGH in values:
            self._value = HIGH
        elif GND in values:
            self._value = GND
        else:
            self._value = OPEN

        for p in self.inport:
            p.value = self.value

    def calc_output(self):
        for p in self.outport:
            p.value = self.value


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





import unittest

class TestJunction(unittest.TestCase):
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
        self.assertEqual(brn.ninport, 3)
        self.assertEqual(brn.noutport, 3)

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
                # print(strof(p1.value), strof(p2.value), strof(p3.value), end=' -> ')
                # print(strof(q1.value), strof(q2.value), strof(q3.value))
                # print(brn)
                self.assertEqual(brn.value, io[i][1])
                self.assertEqual(q1.value, brn.value)
                self.assertEqual(q2.value, brn.value)
                self.assertEqual(q3.value, brn.value)
            except NotImplementedError:
                self.assertEqual(io[i][1], SHORT_CIRCUIT)
    
    def test_branch_no_input(self):
        print('test_branch_no_input')
        
        from Gate import Buffer

        class Dev(SimulatedCircuit):
            def __init__(self, name):
                self.brn = Branch('brn')
                self.bf = [Buffer('bf0'), Buffer('bf1')]

                self.brn >> self.bf[0].I
                self.brn >> self.bf[1].I

                self.update_sequence = [self.brn, self.bf[0], self.bf[1]]

                self.I = self.brn
                self.O = [self.bf[0].O, self.bf[1].O]
            
                super().__init__('Dev', name)
        
        bf1 = Buffer('bf1')
        dev = Dev('dev')
        bf2 = Buffer('bf2')
        bf1.power_on()
        dev.power_on()
        bf2.power_on()

        dev.O[0] >> bf2.I # Branch acts like input Port

        dev.I.value = HIGH
        dev.step()
        bf2.step()
        self.assertEqual(bf2.O.value, HIGH)

        dev.I.value = OPEN
        dev.step()
        bf2.step()
        self.assertEqual(bf2.O.value, OPEN)

        dev.I.set()
        dev.step()
        bf2.step()
        self.assertEqual(bf2.O.value, HIGH)

        dev.I.reset()
        dev.step()
        bf2.step()
        self.assertEqual(bf2.O.value, OPEN)

        bf1.O >> dev.I

        bf1.I.set()
        bf1.step()
        dev.step()
        bf2.step()
        self.assertEqual(bf2.O.value, HIGH)

        bf1.I.reset()
        bf1.step()
        dev.step()
        bf2.step()
        self.assertEqual(bf2.O.value, OPEN)
    
    def test_branch_no_output(self):
        print('test_branch_no_output')
        
        from Gate import Buffer

        class Dev(SimulatedCircuit):
            def __init__(self, name):
                self.bf = [Buffer('bf0'), Buffer('bf1')]
                self.brn = Branch('brn')

                self.bf[0].O >> self.brn
                self.bf[1].O >> self.brn

                self.update_sequence = [self.bf[0], self.bf[1], self.brn]

                self.I = [self.bf[0].I, self.bf[1].I]
                self.O = self.brn
            
                super().__init__('Dev', name)
        
        bf1 = Buffer('bf1')
        dev = Dev('dev')
        bf2 = Buffer('bf2')
        bf1.power_on()
        dev.power_on()
        bf2.power_on()

        bf1.O >> dev.I[0]
        dev.O >> bf2.I # Branch acts like output Port

        bf1.I.set()

        bf1.step()
        dev.step()
        bf2.step()

        self.assertEqual(bf2.O.value, HIGH)
    
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

    suite = unittest.TestSuite()
    suite.addTests([
        TestJunction('test_branch'),
        TestJunction('test_branch_no_input'),
        TestJunction('test_branch_no_output'),
        TestJunction('test_split'),
        TestJunction('test_split8'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
