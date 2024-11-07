
# Binary Bit Value
BitValue = int
HIGH =  1 # closed to high
OPEN =  0 # open
GND  = -1 # closed to ground

BITVALUES = [HIGH, OPEN, GND]

def strof(bitvalue):
    if bitvalue == HIGH:
        return 'HIGH'
    elif bitvalue == GND:
        return 'GND '
    elif bitvalue == OPEN:
        return 'OPEN'
    else:
        raise(ValueError)

