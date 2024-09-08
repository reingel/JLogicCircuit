from abc import *


class Device:
    def __init__(self, device_name, name, n=2):
        self.device_name = device_name
        self.name = name

        # self.step(n)

    def __repr__(self):
        return f'{self.device_name}({self.name})'

    # @abstractmethod
    # def calc_output(self):
    #     pass

    # @abstractmethod
    # def update_state(self):
    #     pass

    def update_inports(self):
        if hasattr(self, 'inports'):
            for inport in self.inports:
                inport.update_value()
    
    def calc_output(self):
        if hasattr(self, 'devices'):
            for device in self.devices:
                device.update_inports()
                device.calc_output()
        
    def update_state(self):
        if hasattr(self, 'devices'):
            for device in self.devices:
                device.update_state()
    
    def step(self, n=1):
        for i in range(n):
            # self.update_inports()
            self.calc_output()
            self.update_state()
