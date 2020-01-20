#import gopigo
import random

#import controller.aruco as aruco
import NetworkEmulator.netemuclient as netemuclient

"""Data received from network
"""
def recv(data:bytes, rssi:int):
    print(rssi, data)

"""Get information of net position and update the network emulator
Returns tupe with:
    north, east, south, west: True if wall, False if open
    final: True if exit of maze
"""
def newPosition(markerID:int):
    global network
    x = markerID&0x0f
    y = (markerID/16)&0x0f
    info = network.maze.getInfo((x, y))
    network.position(float(x), float(y))
    return info

def main():
    global network
    # Setting up network emulator
    # Read server ip from server.ip
    # Connect to network emulator server
    # Receive the maze
    position = random.randint(0,15), random.randint(0,15)
    network = netemuclient.NetEmuClient.connect(recv, position)

    while True:
        i=input()
        network.send(bytes(i, 'utf-8'))
        # print(aruco.get_result())

if __name__ == "__main__":
    try:
        main()
    #     gopigo.stop()
    except KeyboardInterrupt:
    #     gopigo.stop()
    #     aruco.stop_pls = True 
        pass
