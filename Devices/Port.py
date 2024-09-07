import unittest
from EStatus import *
from Device import Device


class Port:
    def __init__(self, name: str, parent: Device, status=OPEN):
        self.name = name
        self.parent = parent
        self.status = status
        self.connected = []

    def __repr__(self):
        str = f'Port({self.parent.name}.{self.name}, {self.status})'
        if self.connected:
            str += f' <---> Port({self.connected.parent.name}.{self.connected.name}, status = {self.connected.status})'
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
    
    def update_status(self):
        if self.connected:
            self.status = self.connected.status


class TestRelay(unittest.TestCase):
    def test_relay(self):
        dev1 = Device('device', 'dev1')
        dev2 = Device('device', 'dev2')
        p1 = Port('p1', dev1, OPEN)
        p2 = Port('p2', dev2, HIGH)
        p1 >> p2
        print(p1)
        print(p2)

if __name__ == '__main__':
    unittest.main()