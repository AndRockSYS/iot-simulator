from enum import Enum

class Packet(Enum):
    DISC = 0
    DISC_ACK = 1
    DISC_ACK_2 = 2
    SYNC = 3
    SYNC_ACK = 4