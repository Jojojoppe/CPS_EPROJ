import signal
import struct
import random
import time
from tcp import TCPClient
from message import Message

running = True

def close_handler(signal, reserved):
    global running
    running = False

signal.signal(signal.SIGINT, close_handler)

control = TCPClient('130.89.85.192', 8080)
control.start()

x = (random.random()-0.5)*10.0
y = (random.random()-0.5)*10.0

cdat = b'\x01' + struct.pack('<ddd', 1.5, x, y)
cmsg = Message.create(cdat)
control.send(cmsg.packet())

cnt=0
while running:
    time.sleep(0.05)
    x += (random.random()-0.5)*0.5
    y += (random.random()-0.5)*0.5
    cdat = b'\x01' + struct.pack('<ddd', 1.5, x, y)
    cmsg = Message.create(cdat)
    control.send(cmsg.packet())

    cnt+=1
    if cnt==25:
        cnt=0
        ddat = b'\x00\x00' + bytes('Test123', 'utf-8')
        dmsg = Message.create(ddat)
        control.send(dmsg.packet())

control.stop()
