import unittest
from BitValue import *
from SimulatedCircuit import SimulatedCircuit


class Port:
    def __init__(self, name: str, parent: SimulatedCircuit, value=OPEN):
        self.name = name
        self.parent = parent
        self.value = value
        self.connected = []

    def __repr__(self):
        if hasattr(self.parent, 'parent'):
            str = f'Port({self.parent.parent.name}.{self.parent.name}.{self.name}, {strof(self.value)})'
            if self.connected:
                str += f' <---> Port({self.connected.parent.parent.name}.{self.connected.parent.name}.{self.connected.name}, {strof(self.connected.value)})'
        else:
            str = f'Port({self.parent.name}.{self.name}, {strof(self.value)})'
            if self.connected:
                str += f' <---> Port({self.connected.parent.name}.{self.connected.name}, {strof(self.connected.value)})'
        return str
    
    def connect(self, port):
        if self.connected:
            return
        if isinstance(port, Port):
            self.connected = port
        else:
            raise(RuntimeError)
        port.connect(self)
    
    def __rshift__(self, port):
        self.connect(port)
    
    def update_value(self):
        if self.connected:
            self.value = self.connected.value
            # if self.value == OPEN:
            #     self.value = self.connected.value
            # else: # self.value == HIGH or self.value == GND:
            #     if self.connected.value == OPEN:
            #         self.connected.value = self.value
            #     elif self.value != self.connected.value:
            #         print('Short circuit !!!')
            #         raise(NotImplementedError)
            #     else: # self.value == self.connected.value
            #         pass


class TestRelay(unittest.TestCase):
    def update_print(self, p1, p2):
        print(p1)
        print('p1 is updated.')
        p1.update_value()
        print(p1)
        print('p2 is updated.')
        p2.update_value()
        print(p1)
        print('---')

    def test_relay(self):
        dev1 = And('and1')
        dev2 = And('and2')
        p1 = Port('p1', dev1)
        p2 = Port('p2', dev2)
        p1 >> p2

        for v1 in [HIGH, GND, OPEN]:
            for v2 in [HIGH, GND, OPEN]:
                try:
                    p1.value = v1
                    p2.value = v2
                    self.update_print(p1, p2)
                except NotImplementedError:
                    print(' ')
        

if __name__ == '__main__':
    from Gate import And

    unittest.main()