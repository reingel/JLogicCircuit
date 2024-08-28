from Unit import *


class Port:
    def __init__(self):
        self.__volt = 0*V

    def __repr__(self):
        return f'Port(volt = {self.volt} V)'
    
    @property
    def volt(self):
        return self.__volt
    
    def set_volt(self, volt: float):
        self.__volt = volt


if __name__ == '__main__':
    p = Port()
    print(p)
    print(p.volt)
    p.set_volt(5*V)
    print(p)
