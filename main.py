import gopigo
import random

import controller.aruco as aruco
import NetworkEmulator.netemuclient as netemuclient


def recv(data:bytes, rssi:int):
    print(rssi, data)

def main():
    # Setting up network emulator
    # Read server ip from server.ip
    # Connect to network emulator server
    # Receive the maze
    ip, port = "", 8080
    with open("server.ip") as f:
        ip = f.read()
    network = netemuclient.NetEmuClient(recv, ip, port)
    network.start()
    network.waitForMaze()

    x = random.randint(0,15)
    y = random.randint(0,15)
    network.position(x, y)
    network.txpower(0.4)

    while True:
        i=input()
        network.send(bytes(i, 'utf-8'))
        print(aruco.get_result())

if __name__ == "__main__":
    try:
        main()
        #gopigo.stop()
    except KeyboardInterrupt:
        gopigo.stop()
        aruco.stop_pls = True 
