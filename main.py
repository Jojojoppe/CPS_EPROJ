import gopigo
import random
import time
import controller.aruco as aruco
import NetworkEmulator.netemuclient as netemuclient


base_speed = 150
kp = 100


def get_control_out(p0):
    # P controller
    # P_out = P0 + Kp * e
    # Per wheel assume that P0 is a constant for driving spesified in this file

    global base_speed
    error = p0 - 0.5 # Deviation from middle
    
    left  = base_speed + kp * error
    right = base_speed - kp * error
    return left, right


def drive_forwards(target):
    left, right = get_control_out(target)
    # print(target, "left", int(left),"right", int(right))

    gopigo.set_left_speed(int(left))
    gopigo.set_right_speed(int(right))


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
    gopigo.set_left_speed(0)
    gopigo.set_right_speed(0)
    gopigo.fwd()
    prev_marker = -1

    lastID = None
    while True:

        # Read aruco marker and update position if neccessary
        (marker, t) = aruco.get_result()
        res = aruco.get_result()
        if merker!=None and lastID!=int(merker):
            # Update position
            lastID = int(marker)
            newPosition(lastID)


        # Get the aruco id and the control base
        print(t)
        if marker != None: marker = int(marker)

        if marker == None or marker == -1:
            drive_forwards(t)

        elif marker != prev_marker:
            prev_marker = marker
            print("stop", marker)
            gopigo.set_left_speed(0)
            gopigo.set_right_speed(0)
            gopigo.stop()
            time.sleep(1)
            gopigo.fwd()
        else:
            drive_forwards(t)

    main()



if __name__ == "__main__":
    try:
        main()
        gopigo.stop()
    except KeyboardInterrupt:
        gopigo.stop()
        aruco.stop_pls = True 
    except Exception:
        main()
