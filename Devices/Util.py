import numpy as np
from EStatus import *

def bool2int(status):
    if isinstance(status, EStatus):
        return int(1) if status else int(0)
    elif isinstance(status, np.ndarray):
        return np.array([int(x) for x in status])


if __name__ == '__main__':
    a = bool2int(HIGH)
    print(a)
    b = bool2int(np.array([HIGH, OPEN, OPEN]))
    print(b)