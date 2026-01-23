from enum import Enum

class Mode(Enum):
    IDLE = 0
    STANDBY = 1
    RECEIVE = 2
    DECODE = 3
    TRANSMIT = 4