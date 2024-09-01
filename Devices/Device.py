from abc import *


class Device:
    def __init__(self, name):
        self.name = name
        self.step()
        self.step()

    def __repr__(self):
        return f'Device({self.name})'

    @abstractmethod
    def calc_output(self):
        pass

    @abstractmethod
    def update(self):
        pass

    def step(self):
        for i in range(2):
            self.calc_output()
            self.update()
