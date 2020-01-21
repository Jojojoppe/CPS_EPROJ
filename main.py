import gopigo
import random
import time
import controller.aruco as aruco
import controller.space as space
import NetworkEmulator.netemuclient as netemuclient
from enum import Enum


base_speed = 130
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
    time.sleep(0.001)
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
    # global network
    # x = markerID&0x0f
    # y = (markerID//16)&0x0f
    # info = network.maze.getInfo((x, y))
    # network.position(float(x), float(y))
    # return info
    if markerID==3:
        return (False, True, False, True, False)
    elif markerID==4:
        return (True, False, False, True, False)
    else:
        return (False, False, False, False, True)


def get_turn(m):
    return "right"

def do_turn(direction):
    if direction == "left":
        pass


    else:
        pass


def turn_done():

    return False



class State(Enum):
    DRIVE = 1
    TURN_RIGHT = 2
    TURN_LEFT = 3
    STOP = 4

state = State.DRIVE
state_timer = time.time()
prev_marker = -1

def change_state(m, t):
    global state, prev_marker, state_timer
    new_state = State.STOP

    if state == State.DRIVE:
        if m == None or m == -1:
            new_state = State.DRIVE
        elif m >= 0 and m != prev_marker:
            new_state = State.STOP
        else:
            new_state = State.DRIVE

    elif state == State.STOP:
        if time.time() - 1 > state_timer:
            direction = get_turn(m)
            if direction == "left":
                new_state = State.TURN_LEFT
            elif direction == "right":
                new_state = State.TURN_RIGHT
            else: 
                new_state = State.DRIVE
        else:
            new_state = State.STOP

    elif state == State.TURN_LEFT:
        if turn_done():
            new_state = State.DRIVE
        else:
            new_state = State.TURN_LEFT

    elif state == State.TURN_RIGHT:
        if turn_done():
            new_state = State.DRIVE
        else:
            new_state = State.TURN_RIGHT

    if new_state != state:
        state_timer = time.time()

    return new_state


def main():
    global network, state, prev_marker
    # position = random.randint(0,15), random.randint(0,15)
    # network = netemuclient.NetEmuClient.connect(recv, position)
    time.sleep(2)
    gopigo.set_left_speed(0)
    gopigo.set_right_speed(0)
    gopigo.fwd()
    prev_marker = -1

    lastID = None
    while True:

        # Read aruco marker and update position if neccessary
        (marker, t) = aruco.get_result()
        # res = aruco.get_result()
        # if merker!=None and lastID!=int(merker):
        #     # Update position
        #     lastID = int(marker)
        #     newPosition(lastID)


        # Get the aruco id and the control base
        # print(t)
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
