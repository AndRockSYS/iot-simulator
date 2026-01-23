RANGE = 800 # Range for all devices in meters
LOW_POWERED_NODES = 18 # Low powered nodes
HIGH_POWERED_NODES = 36 # High powered nodes
NODES = LOW_POWERED_NODES + HIGH_POWERED_NODES # Amount of nodes in the simulation

ONE_DAY = 86_400_000 # Miliseconds in one day
SIM_TIME = 14 * ONE_DAY # Simulation time in miliseconds
SUNRISE_TIME = 8 * 60 * 60 * 1_000 # Time of sunrise in miliseconds
SUNSET_TIME = 18 * 60 * 60 * 1_000 # Time of sunset in miliseconds
IS_DAY_CYCLE = False # Is simulation using day cycle or charges infinitely

PT_TIME = 14.89 # Time in miliseconds used for decoding an incoming packet
PT_LOSS = 0.005 # Chance of loosing a packet
PROP_DELAY_RANGE = (10, 50) # Packet propagation delay in miliseconds

# All the energy is Joules or Joules/miliseconds
E_MAX = 8.82 # Maximum used energy
E_TRESHOLD = 1.62 # Threshold for energy capacity
E_IDLE =  0.00000495 / 1_000 # Energy used in idle mode per millisecond
E_RECEIVE = 0.03564 / 1_000 # Energy used per millisecond in receiveing mode
E_TX = 0.1023 / 1_000 * PT_TIME # Energy used to transmit the packet
E_RX = E_RECEIVE * PT_TIME # Energy used to receive and decode the packet

LISTEN_TIME_RANGE = (1_000, 2_000) # Range for time listening in milliseconds

SYNC_INTERVAL = 7 * ONE_DAY # How ofter nodes perform sync
SYNC_TIME = 30_000 # For how long sync is operated
SYNC_TIME_RANGE = (2, SYNC_TIME / 2) # For how long node listens for a sync message, before sending one
SYNC_PREPARATION_TIME = 45 * 60 * 1_000 # For how long before a sync node starts chraging

CLOCK_DRIFT_PER_DAY = 1_730 # Max clock drift per day
CLOCK_DRIFT_MULTIPLIER_RANGE = (
    (ONE_DAY - CLOCK_DRIFT_PER_DAY) / ONE_DAY,
    (ONE_DAY + CLOCK_DRIFT_PER_DAY) / ONE_DAY
) # Range for time multiplier for current clock drift time range

HIGH_LIGHT_RANGE_LUX = (30, 35) # Number of lux for a high powered device
LOW_LIGHT_RANGE_LUX = (15, 20) # Number of lux for a low powered device
