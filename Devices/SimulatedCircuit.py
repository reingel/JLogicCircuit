from abc import *


class SimulatedCircuit:
    def __init__(self, device_name, name, n=2):
        self.device_name = device_name
        self.name = name

    def __repr__(self):
        return f'{self.device_name}({self.name})'

    def update_inport(self):
        if hasattr(self, 'inports'):
            for inport in self.inports:
                inport.update_value()
    
    def calc_output(self):
        if hasattr(self, 'subdevices'):
            for device in self.subdevices:
                device.update_inport()
                device.calc_output()
        
    def update_state(self):
        if hasattr(self, 'subdevices'):
            for device in self.subdevices:
                device.update_state()
    
    def step(self, n=1):
        for i in range(n):
            self.update_inport()
            self.calc_output()
            self.update_state()
