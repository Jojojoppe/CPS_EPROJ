import struct
import math
from message import Message
from packet_loss import packet_loss

class Node():
    def __init__(self, nodes, message_buffer, index, config):
        self.tx_power = 0.0
        self.position = (0.0, 0.0)

        self.nodes = nodes                      # Global nodes dictionary
        self.message_buffer = message_buffer    # Sending message buffer array
        self.index = index                      # Index of self in nodes dictionary
        self.config = config                    # Config dictionary

        self.loss = float(config.get('radio', 'loss', fallback='0.0'))
        self.noise_floor = float(config.get('radio', 'noise_floor', fallback='-80.0'))
        self.packet_loss_function = config.get('radio', 'packet_loss_function', fallback='none')
        self.precalcFSPL()

        self.rx_dat = False
        self.rx_ctl = False

        self.tx_list = []

    # Data message is received
    def on_data_message(self, msg:bytes):
        self.rx_dat = True
        self.tx_list = []
        # rssi = int(msg[0]) : not read here: must be calculated at sending to other nodes
        data = msg[1:]
        
        # Loop over nodes
        for index, node in self.nodes.items():
            if index==self.index:
                continue
            # Calculate distance
            nx,ny = node.position
            mx,my = self.position
            dist = math.sqrt((nx-mx)*(nx-mx) + (ny-my)*(ny-my))
            # Calculate RSSI
            rssi = int(node.calcRSSI(dist))
            # If RSSI is bigger then noise floor
            if rssi>self.noise_floor:
                # If packet is received at the other end
                if packet_loss(rssi-self.noise_floor, self.packet_loss_function):
                    d = b'\x00' + struct.pack('b', rssi) + data
                    m = Message.create(d)
                    node.send(m.packet())
                    self.tx_list.append(node.position)

    # Control message is received
    def on_control_message(self, msg:bytes):
        self.rx_ctl = True
        s = struct.unpack('<ddd', msg)
        self.tx_power = s[0]
        self.position = (s[1], s[2])
        self.precalcFSPL()

    # Send a message to this node
    def send(self, msg:Message):
        if self.config.get('logging', 'rec_msg', fallback='true')=='true':
            print('[%s] rec: %s'%(str(self.index), str(msg)))
        self.message_buffer.append(msg)

    # Calculate part of free space path loss
    def precalcFSPL(self):
        Dt = float(self.config.get('radio', 'directivity_transmitter', fallback='1.0'))
        Dr = float(self.config.get('radio', 'directivity_receiver', fallback='1.0'))
        wavelength = float(self.config.get('radio', 'wavelength', fallback='1000'))/1000
        self.FSPL = self.loss*Dt*Dr*wavelength*wavelength/39.4784176
        if self.config.get('logging', 'FSPL', fallback='false')=='true':
            print("[%s] FSPL=%f"%(self.index, self.FSPL))

    # Calculate Received signal strength
    def calcRSSI(self, distance):
        if distance==0.0:
            FSPL = 1.0
        else:
            FSPL = self.FSPL/(distance*distance)
        rssi = FSPL*self.tx_power
        return 20*math.log10(rssi)

    # Calculate distance from node with specific RSSI
    def calc_dist(self, rssi):
        return math.sqrt((self.FSPL*self.tx_power)/math.pow(10, (rssi/20.0)))