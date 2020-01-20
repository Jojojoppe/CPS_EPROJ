import struct
import threading
import random
import pickle
import sys
from NetworkEmulator.message import Message
from NetworkEmulator.tcp import TCPClient, Timeout
import NetworkEmulator.maze as maze
from NetworkEmulator.maze import Maze, Cell

sys.modules['maze'] = maze

class NetEmuClient(threading.Thread):
    def __init__(self, recv_func, ip, port):
        threading.Thread.__init__(self)
        self.recv_func = recv_func
        self.x = 0.0
        self.y = 0.0
        self.tx = 1.0

        self.maze = None

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
                elif msg.data[0]==2 and self.maze==None:
                    # MAZE recieved
                    self.maze = Maze.loads(msg.data[2:])
                else:
                    # UNKNOWN
                    pass
                # ----------------
                msg = None
                buf = b''

    """Stop receiving thread
    """
    def stop(self):
        self.running = False

    """Broadcast packet
    """
    def send(self, packet=b''):
        ddat = b'\x00\x00' + packet
        dmsg = Message.create(ddat)
        self.client.sendall(dmsg.packet())

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
        self.client.sendall(cmsg.packet())

    """Wait for maze to be received
    """
    def waitForMaze(self):
        while self.maze==None:
            pass

    @classmethod
    def connect(cls, recv, position):
        ip, port = "", 8080
        with open("server.ip") as f:
            ip = f.read()
        network = NetEmuClient(recv, ip, port)
        network.start()
        network.waitForMaze()

        network.position(*position)
        network.txpower(0.4)
        return network