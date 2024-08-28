from abc import *


class Device:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Device({self.name})'

    @abstractmethod
    def calc_output(self):
        pass

    @abstractmethod
    def update(self):
        pass