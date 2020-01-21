import gopigo
import time

gopigo.set_left_speed(250)
gopigo.set_right_speed(250)
gopigo.left_rot()

time.sleep(1.80)
gopigo.stop()
