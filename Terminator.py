import numpy as np
import matplotlib.pyplot as plt
from Unit import *
from Util import *

class Terminator:
    def __init__(self):
        self.vol = False

    def __repr__(self):
        return f"Terminator({bool2int(self.vol)})"
    
    def vol(self):
        return self.vol


if __name__ == '__main__':
    term = Terminator()
    print(term)
