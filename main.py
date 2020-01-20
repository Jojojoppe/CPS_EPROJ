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
    
    # TODO maybe swap out the signs
    left  = base_speed + kp * error
    right = base_speed - kp * error
    return left, right


def drive_forwards(target):
    left, right = get_control_out(target)
    gopigo.set_left_speed(int(left))
    gopigo.set_right_speed(int(right))
    gopigo.fwd()

def recv(data:bytes, rssi:int):
    print(rssi, data)

def main():
    # Setting up network emulator
    # Read server ip from server.ip
    # Connect to network emulator server
    # Receive the maze
    # ip, port = "", 8080
    # with open("server.ip") as f:
    #     ip = f.read()
    # network = netemuclient.NetEmuClient(recv, ip, port)
    # network.start()
    # network.waitForMaze()

    # x = random.randint(0,15)
    # y = random.randint(0,15)
    # network.position(x, y)
    # network.txpower(0.4)

    while True:
        # i=input()
        # network.send(bytes(i, 'utf-8'))
        print(aruco.get_result())

if __name__ == "__main__":
    try:
        main()
        gopigo.stop()
    except KeyboardInterrupt:
        gopigo.stop()
        aruco.stop_pls = True 
