import controller.aruco as aruco
import gopigo


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


def main():
    while True:
        print(aruco.get_result())






if __name__ == "__main__":
    try:
        main()
        gopigo.stop()
    except KeyboardInterrupt:
        gopigo.stop()
        aruco.stop_pls = True 
