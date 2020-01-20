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
    gopigo.set_left_speed(0)
    gopigo.set_right_speed(0)
    gopigo.fwd()
    prev_marker = -1

    while True:
        # Get the aruco id and the control base
        (marker, t) = aruco.get_result()
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
