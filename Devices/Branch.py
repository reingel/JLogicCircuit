from BitValue import *
from SimulatedCircuit import SimulatedCircuit
from Port import Port
from collections.abc import Iterable


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
    
    def add_inport(self, obj):
        if isinstance(obj, Iterable):
            for p in obj:
                self.add_inport(p)
            return self
        elif isinstance(obj, Port) or isinstance(obj, Branch):
            n = self.ninport
            p = Port(f'inport{n + 1}', self)
            obj >> p
            self.inport.append(p)
            self._ninport += 1
            return self
        elif hasattr(obj, 'O') and (isinstance(obj.O, Port) or isinstance(obj.O, Branch)):
            return self.add_inport(obj.O)
        else:
            raise(NotImplementedError)

    def add_outport(self, obj):
        if isinstance(obj, Iterable):
            for p in obj:
                self.add_outport(p)
            return obj
        elif isinstance(obj, Port) or isinstance(obj, Branch):
            n = self.noutport
            p = Port(f'outport{n + 1}', self)
            p >> obj
            self.outport.append(p)
            self._noutport += 1
            return obj
        elif hasattr(obj, 'I') and (isinstance(obj.I, Port) or isinstance(obj.I, Branch)):
            return self.add_outport(obj.I)
        else:
            raise(NotImplementedError)
    
    def __lshift__(self, obj):
        return self.add_inport(obj)

    def __rshift__(self, obj):
        return self.add_outport(obj)
    
    def __rrshift__(self, obj):
        return self.__lshift__(obj)
    
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
        (p1, p2, p3) >> brn >> (q1, q2, q3)

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

                self.brn >> (self.bf[0], self.bf[1])

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

        dev.O[0] >> bf2 # Branch acts like input Port

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

        bf1 >> dev.I

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

                (self.bf[0], self.bf[1]) >> self.brn

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

        bf1 >> dev.I[0]
        dev.O >> bf2.I # Branch acts like output Port

        bf1.I.set()

        bf1.step()
        dev.step()
        bf2.step()

        self.assertEqual(bf2.O.value, HIGH)
    
    def test_branch_branch(self):
        brn1 = Branch('brn1')
        brn2 = Branch('brn2')

        brn1 >> brn2

if __name__ == '__main__':
    from Gate import And, Buffer

    suite = unittest.TestSuite()
    suite.addTests([
        TestJunction('test_branch'),
        TestJunction('test_branch_no_input'),
        TestJunction('test_branch_no_output'),
        TestJunction('test_branch_branch'),
    ])
    runner = unittest.TextTestRunner()
    runner.run(suite)
