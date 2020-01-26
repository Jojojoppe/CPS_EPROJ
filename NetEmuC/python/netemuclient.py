import struct
import threading
import random
import pickle
import sys
import socket
import struct

class NetEmuClient(threading.Thread):
    """ Create NetEmuClient
    recv_func: receive callback
    ip: ip of server
    port: port of server
    """
    def __init__(self, recv_func, ip:str, port:int):
        threading.Thread.__init__(self)
        self.recv_func = recv_func
        self.ip = ip
        self.port = port

        self.x = 0.0
        self.y = 0.0
        self.txp = 1.0

        self.running = True

        self.maze = {}
        self.mazeDone = False

        # Connect to server
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.socket.settimeout(0.001)
        except Exception as e:
            print("Could not connect to socket or server: %s"%str(e))
            sys.exit(0)

    def waitForMaze(self):
        # Wait for maze
        while not self.mazeDone:
            pass
        print("Maze received")

    def stop(self):
        self.running = False
        self.close()

    def close(self):
        self.socket.close()

    def send(self, data:bytes):
        dat = struct.pack('<I', len(data)+2) + b'\x00\x00' + data
        self.socket.sendall(dat)

    def _sendControl(self):
        dat = struct.pack('<I', 13) + b'\x01' + struct.pack('<fff', self.txp, self.x, self.y)
        self.socket.sendall(dat)

    def position(self, x:float, y:float):
        self.x = x
        self.y = y
        self._sendControl()

    def txpower(self, txp:float):
        self.txp = txp
        self._sendControl()

    def run(self):
        self.running = True
        buf = b''
        packetsize = None
        while True:
            # Receive data
            try:
                dat = self.socket.recv(4096)
            except socket.timeout:
                dat = None
            if dat==b'':
                print("Server disconnected")
                self.stop()
                sys.exit(0)
            elif dat is not None:
                buf += dat

            # If not yet started with reading packet
            # and enough bytes in buffer for packet size
            if packetsize is None and len(buf)>=4:
                packetsize = struct.unpack('<I', buf[0:4])[0]
                buf = buf[4:]

            # Packet size known
            # Receive rest of packet
            elif packetsize is not None and len(buf)>=packetsize:
                if buf[0]==0:
                    # Data packet
                    rssi = struct.unpack('b', buf[1:2])[0]
                    self.recv_func(buf[2:packetsize], rssi)
                elif buf[0]==2:
                    # MAZE PACKET
                    self._receiveMaze(buf[1:packetsize])
                    self.mazeDone = True
                if len(buf)==packetsize:
                    buf=b''
                else:
                    buf = buf[packetsize:]
                packetsize = None

    def _receiveMaze(self, data:bytes):
        while len(data)>0:
            # Get data
            x, y, north, east, south, west, final = struct.unpack("<II?????", data[0:13])
            data = data[13:]
            self.maze[(x,y)] = (north, east, south, west, final)

def r(data:bytes, rssi:int):
    print(data, rssi)

if __name__=="__main__":
    n = NetEmuClient(r, 'localhost', 8080)
    n.start()
    n.waitForMaze()
    x,y = 8,8
    n.position(x,y)
    n.txpower(0.04)
    while True:
        i = input()
        if i=="U":
            x,y = x,y-1
            n.position(x,y)
        elif i=="D":
            x,y = x,y+1
            n.position(x,y)
        elif i=="L":
            x,y = x-1,y
            n.position(x,y)
        elif i=="R":
            x,y = x+1,y
            n.position(x,y)
        else:
            n.send(bytes(i, 'utf-8'))