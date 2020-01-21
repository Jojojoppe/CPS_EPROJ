import gopigo
import time
import aruco


gopigo.set_left_speed(250)
gopigo.set_right_speed(250)
gopigo.left_rot()

time.sleep(1.60)



while True:
    gopigo.stop()
    time.sleep(0.2)
    marker, t = aruco.get_result()
    if t > 0.01:
        break
    gopigo.set_left_speed(250)
    gopigo.set_right_speed(250)
    gopigo.left_rot()

    time.sleep(0.8)


gopigo.stop()
