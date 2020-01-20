import gopigo
import random

import controller.aruco as aruco
import NetworkEmulator.netemuclient as netemuclient


# P controller
# P_out = P0 + Kp * e
# Per wheel assume that P0 is a constant for driving spesified in this file


base_speed = 230
kp = 55


def get_control_out(target):
    global base_speed
    error = target - 0.5 # Deviation from middle
    
    left  = base_speed + kp * error
    right = base_speed - kp * error
    return left, right


def drive_forwards(target):
    left, right = get_control_out(target)
    gopigo.set_left_speed(int(left))
    gopigo.set_right_speed(int(right))
    gopigo.fwd()


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
    y = (markerID//16)&0x0f
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

    lastID = None
    while True:

        # Read aruco marker and update position if neccessary
        res = aruco.get_result()
        if res[0]!=None and lastID!=int(res[0]):
            # Update position
            lastID = int(res[0])
            newPosition(lastID)


if __name__ == "__main__":
    try:
        main()
        gopigo.stop()
    except KeyboardInterrupt:
        gopigo.stop()
        aruco.stop_pls = True 
