# Nodes configurations
RANGE = 800 # Range for all devices in meters
LOW_POWERED_NODES = 18 # Low powered nodes
HIGH_POWERED_NODES = 36 # High powered nodes
NODES = LOW_POWERED_NODES + HIGH_POWERED_NODES # Amount of nodes in the simulation
HIGH_LIGHT_RANGE_LUX = (200, 1000) # Number of lux for a high powered device
LOW_LIGHT_RANGE_LUX = (100, 200) # Number of lux for a low powered device

# Simulation dutation
ONE_DAY = 86_400_000 # Miliseconds in one day
SIM_TIME = 15 * ONE_DAY # Simulation time in miliseconds

# Network timings
PT_TIME = 14.89 # Time in miliseconds used for decoding an incoming packet
PT_LOSS = 0.005 # Chance of loosing a packet
PROP_DELAY_RANGE = (100, 500) # Packet propagation delay in miliseconds

# Energy in J or J/ms
E_MAX = 8.82 # Maximum used energy
E_TRESHOLD = 1.62 # Threshold for energy capacity
E_IDLE =  0.00000495 / 1_000 # Energy used in idle mode per millisecond
E_RECEIVE = 0.03564 / 1_000 # Energy used per millisecond in receiveing mode
E_TX = 0.1023 / 1_000 * PT_TIME # Energy used to transmit the packet
E_RX = E_RECEIVE * PT_TIME # Energy used to receive and decode the packet

# Window durations for phases
DISC_LISTEN_RANGE = (1_000, 2_000) # Range for time listening in milliseconds
SYNC_LISTEN_TIME = 30_000 # For how long sync is operated
SYNC_TIME_RANGE = (1_000, SYNC_LISTEN_TIME / 2) # For how long node listens for a sync message, before sending one
SYNC_PREPARATION_TIME = 30 * 60 * 1_000 # For how long before a sync node starts chraging

# Clock Drift
CLOCK_DRIFT_PER_DAY = 1_730 # Max clock drift per day
CLOCK_DRIFT_MULTIPLIER_RANGE = (
    (ONE_DAY - CLOCK_DRIFT_PER_DAY) / ONE_DAY,
    (ONE_DAY + CLOCK_DRIFT_PER_DAY) / ONE_DAY
) # Range for time multiplier for current clock drift time range