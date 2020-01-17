import struct
import threading
import random
from message import Message
from tcp import TCPClient

class NetEmuClient(threading.Thread):
    def __init__(self, recv_func, ip, port):
        threading.Thread.__init__(self)
        self.recv_func = recv_func
        self.x = 0.0
        self.y = 0.0
        self.tx = 1.0

        self.client = TCPClient(ip, port)
        self.client.start()
        self._sendControl()

    """Run receiving thread
    """
    def run(self):
        # Buffer to fill
        buf = b''
        # Message object
        msg = None

        self.running = True
        while self.running:
            # Receive data
            dat = self.client.recv_timeout(4096, 0.1)
            if dat!=None and dat!=b'':
                buf += dat
            elif dat==b'':
                # Server disconnected
                pass
            # Create message object
            if msg==None:
                msg, buf = Message.recreate(buf)
            elif not msg.done:
                buf = msg.finish(buf)
            if msg!=None and msg.done:
                # Message received
                # ----------------
                if msg.data[0]==0:
                    # DATA received
                    rssi = struct.unpack('b', msg.data[1:2])[0]
                    self.recv_func(msg.data[2:], rssi)
                else:
                    # UNKNOWN
                    pass
                # ----------------
                msg = None

    """Stop receiving thread
    """
    def stop(self):
        self.running = False

    """Broadcast packet
    """
    def send(self, packet=b''):
        ddat = b'\x00\x00' + packet
        dmsg = Message.create(ddat)
        self.client.send(dmsg.packet())

    """Update position
    """
    def position(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self._sendControl()

    """Update transmission power
    """
    def txpower(self, txp=1.0):
        self.tx = txp
        self._sendControl()

    """Send control message
    """
    def _sendControl(self):
        cdat = b'\x01' + struct.pack('<ddd', self.tx, self.x, self.y)
        cmsg = Message.create(cdat)
        self.client.send(cmsg.packet())

def recv(packet=b'', rssi=0):
    print(rssi, packet)

if __name__=="__main__":

    # Get server IP
    f=open('../server.ip')
    ip=f.read()
    f.close()

    x = (random.random()-0.5)*16.0
    y = (random.random()-0.5)*16.0

    cl = NetEmuClient(recv, ip, 8080)
    cl.start()
    cl.position(x, y)
    cl.txpower(0.1)

    while True:
        i=input()
        cl.send(bytes(i, 'utf-8'))