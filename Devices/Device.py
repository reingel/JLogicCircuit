from abc import *


class Device:
    def __init__(self, name):
        self.name = name
        self.step(n=2)

    def __repr__(self):
        return f'Device({self.name})'

    @abstractmethod
    def calc_output(self):
        pass

    @abstractmethod
    def update_state(self):
        pass

    def step(self, n=1):
        for i in range(n):
            self.calc_output()
            self.update_state()
