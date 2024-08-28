from Unit import *
from Util import *


class Port:
    def __init__(self, name: str, volt=False):
        self.__name = name
        self.__volt = volt
        self.__connected = []

    def __repr__(self):
        return f'Port(name = {self.name}, volt = {bool2int(self.volt)}, connected_port = {self.connected.name})'

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
    
    def connect(self, port):
        if self.connected:
            return
        if isinstance(port, Port):
            self.__connected = port
        else:
            raise(RuntimeError)
        port.connect(self)


if __name__ == '__main__':
    p1 = Port('p1', False)
    p2 = Port('p2', True)
    p1.connect(p2)
    print(p1)
    print(p2)
