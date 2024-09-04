from EStatus import *
from Util import *
from Device import Device


class Port:
    def __init__(self, name: str, parent: Device, status=OPEN):
        self.__name = name
        self.__parent = parent
        self.status = status
        self.__connected = []

    def __repr__(self):
        return f'Port({self.__parent.name}.{self.name}, status = {bool2int(self.status)})'

    @property
    def name(self):
        return self.__name
    
    @property
    def connected(self):
        return self.__connected
    
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
            self.status = self.connected.status


if __name__ == '__main__':
    dev1 = Device('dev1')
    p1 = Port('p1', dev1, OPEN)
    p2 = Port('p2', dev1, HIGH)
    p1 >> p2
    print(p1)
    print(p2)
