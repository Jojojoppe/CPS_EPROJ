# Function which defines if packet is dropped
# SNR: distance between noise floor and RSSI in dBm
# Returns true if packet should be passed
def packet_loss(self, SNR=0, func='none'):
    if(func=='none'):
        return True
    else:
        raise Exception('%s packet loss function not known')