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
        else:
            for i in range(n):
                if hasattr(self, 'update_inport'):
                    self.update_inport()
                if hasattr(self, 'update_state'):
                    self.update_state()
                if hasattr(self, 'calc_output'):
                    self.calc_output()
