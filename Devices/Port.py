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
        str = f'Port({self.parent.name}.{self.name}, {self.value})'
        if self.connected:
            str += f' <---> Port({self.connected.parent.name}.{self.connected.name}, value = {self.connected.value})'
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


class TestRelay(unittest.TestCase):
    def test_relay(self):
        dev1 = And('and1')
        dev2 = And('and2')
        rly1 = Relay('rly1', dev1)
        rly2 = Relay('rly2', dev2)
        p1 = Port('p1', dev1, OPEN)
        p2 = Port('p2', dev2, HIGH)
        p1 >> p2
        print(p1)
        print(p2)

if __name__ == '__main__':
    from Gate import And
    from Relay import Relay

    unittest.main()