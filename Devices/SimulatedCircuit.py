from abc import *


class SimulatedCircuit:
    def __init__(self, device_name, name, n=1):
        self.device_name = device_name
        self.name = name

    def __repr__(self):
        return f'{self.device_name}({self.name})'

    def power_on(self):
        if hasattr(self, 'update_sequence'):
            for device in self.update_sequence:
                device.power_on()
        elif hasattr(self, 'on'):
            self.on()

    def power_off(self):
        if hasattr(self, 'update_sequence'):
            for device in self.update_sequence:
                device.power_off()
        elif hasattr(self, 'off'):
            self.off()

    def step(self, n=1):
        if hasattr(self, 'update_sequence'):
            for device in self.update_sequence:
                device.step()
                a=1
        else:
            for i in range(n):
                self.update_inport()
                self.update_state()
                self.calc_output()
                a=1
