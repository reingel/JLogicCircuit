from abc import *


class Device:
    def __init__(self, name):
        self.name = name
        self.step(n=2)

    def __repr__(self):
        return f'Device({self.name})'

    # @abstractmethod
    # def calc_output(self):
    #     pass

    # @abstractmethod
    # def update_state(self):
    #     pass
    
    def calc_output(self):
        for device in self.devices:
            device.calc_output()
        
    def update_state(self):
        for device in self.devices:
            device.update_state()
    
    def step(self, n=1):
        for i in range(n):
            self.calc_output()
            self.update_state()
