import gopigo
import random
import time
import controller.aruco as aruco
import controller.space as space
import NetworkEmulator.netemuclient as netemuclient
from enum import Enum


base_speed = 150
kp = 120
turn_angle = 85


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
        return (True, True, False, True, False)
    elif markerID==4:
        return (True, True, False, True, False)
    else:
        return (False, True, False, True, False)


def get_turn(m):
    m_info = newPosition(m)
    # (north, east, south, west, final_pos)
    # TODO Add algorithm decision making here

    # For now find first open wall clockwise from north
    dirs = ["straight", "right", "around", "left"]
    for i in range(4):
        if not m_info[i]:
            return dirs[i]

    return "straight"

def do_turn(direction):
    gopigo.set_left_speed(250)
    gopigo.set_right_speed(250)
    global turn_angle
    time.sleep(0.1)
    if direction == "left":
        gopigo.turn_left_wait_for_completion(turn_angle)
    elif direction == "around":
        gopigo.set_left_speed(250)
        gopigo.set_right_speed(250)
        gopigo.left_rot()

        time.sleep(1.80)
        gopigo.stop()
    else:
        gopigo.turn_right_wait_for_completion(turn_angle)
    print("Turn done")
    time.sleep(0.1)
    gopigo.fwd()
    drive_forwards(0.5)

def turn_done():

    return True



class State(Enum):
    DRIVE = 1
    TURN_RIGHT = 2
    TURN_LEFT = 3
    STOP = 4
    TURN_AROUND = 5

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
        prev_marker = m
        if time.time() - 1 > state_timer:
            direction = get_turn(m)
            print("dir:", direction)
            if direction == "left":
                new_state = State.TURN_LEFT
            elif direction == "right":
                new_state = State.TURN_RIGHT
            elif direction == "around":
                new_state = State.TURN_AROUND
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

    elif state == State.TURN_AROUND:
        if turn_done():
            new_state = State.DRIVE
        else:
            new_state = State.TURN_AROUND

    if new_state != state:
        print(new_state, m)
        # TODO make better
        if state == State.STOP and new_state == State.DRIVE:
            gopigo.fwd()
        state_timer = time.time()

    return new_state


def main():
    global network, state, prev_marker
    # position = random.randint(0,15), random.randint(0,15)
    # network = netemuclient.NetEmuClient.connect(recv, position)
    time.sleep(1)
    gopigo.set_left_speed(0)
    gopigo.set_right_speed(0)
    gopigo.fwd()
    
    print(state)
    while True:

        (marker, t) = aruco.get_result()
        state = change_state(marker, t)

        if state == State.DRIVE:
            drive_forwards(t)
            pass

        elif state == State.STOP:
            gopigo.stop()

        elif state == State.TURN_LEFT:
            do_turn("left")

        elif state == State.TURN_RIGHT:
            do_turn("right")
        elif state == State.TURN_AROUND:
            do_turn("around")
            time.sleep(0.001)
        else:
            raise ValueError


if __name__ == "__main__":
    try:
        main()
        gopigo.stop()
    except KeyboardInterrupt:
        gopigo.stop()
        aruco.stop() 
    except Exception:
        main()
