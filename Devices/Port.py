from Constant import *
from Util import *
from Device import Device


class Port:
    def __init__(self, name: str, parent: Device, volt=LOW):
        self.__name = name
        self.__parent = parent
        self.__volt = volt
        self.__connected = []

    def __repr__(self):
        return f'Port({self.__parent.name}.{self.name}, state = {bool2int(self.volt)})'

    @property
    def name(self):
        return self.__name
    
    @property
    def volt(self):
        return self.__volt
    
    @property
    def connected(self):
        return self.__connected
    
    def set_volt(self, volt):
        if isinstance(volt, bool):
            self.__volt = volt
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
            self.set_volt(self.connected.volt)


if __name__ == '__main__':
    dev1 = Device('dev1')
    p1 = Port('p1', dev1, LOW)
    p2 = Port('p2', dev1, HIGH)
    p1 >> p2
    print(p1)
    print(p2)