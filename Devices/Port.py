from BitValue import *
from Util import *
from Device import Device


class Port:
    def __init__(self, name: str, parent: Device, value=LOW):
        self.__name = name
        self.__parent = parent
        self.__value = value
        self.__connected = []

    def __repr__(self):
        return f'Port({self.__parent.name}.{self.name}, state = {bool2int(self.value)})'

    @property
    def name(self):
        return self.__name
    
    @property
    def value(self):
        return self.__value
    
    @property
    def connected(self):
        return self.__connected
    
    def set_value(self, value):
        if isinstance(value, BitValue):
            self.__value = value
        else:
            raise(RuntimeError)
    
    def __connect(self, port):
        if self.connected:
            return
        if isinstance(port, Port):
            self.__connected = port
        else:
            raise(RuntimeError)
        port.__connect(self)
    
    def __rshift__(self, port):
        self.__connect(port)
    
    def update(self):
        if self.connected:
            self.set_value(self.connected.value)


if __name__ == '__main__':
    dev1 = Device('dev1')
    p1 = Port('p1', dev1, LOW)
    p2 = Port('p2', dev1, HIGH)
    p1 >> p2
    print(p1)
    print(p2)
