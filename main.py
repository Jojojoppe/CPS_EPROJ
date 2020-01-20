import controller.aruco as aruco
import gopigo











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
