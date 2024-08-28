import numpy as np

def bool2int(value):
    if isinstance(value, bool):
        return int(1) if value else int(0)
    elif isinstance(value, np.ndarray):
        return np.array([int(x) for x in value])


if __name__ == '__main__':
    a = bool2int(True)
    print(a)
    b = bool2int(np.array([True, False, False]))
    print(b)