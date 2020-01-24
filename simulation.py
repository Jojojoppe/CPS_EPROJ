import random
import time
import NetEmuC.python.netemuclient as netemuclient
import algorithm.algo as algo

algoInstance = None

"""Data received from network
"""
def rec(data:bytes, rssi:int):
    global algoInstance
    algoInstance.recv(data, rssi)


"""Get information of net position and update the network emulator
Returns tupe with:
    north, east, south, west: True if wall, False if open
    final: True if exit of maze
"""
def newPosition(x,y):
    global network, algoInstance
    info = network.maze[(x, y)]
    network.position(float(x), float(y))
    algoInstance.newPos((x, y), info)
    return info


def main():
    global network, algoInstance
    # Setting up network emulator
    # Read server ip from server.ip
    # Connect to network emulator server
    # Receive the maze
    x,y = 4, 0
    network = netemuclient.NetEmuClient(rec, "localhost", 8080)
    network.start()
    network.waitForMaze()
    network.position(x, y)
    network.txpower(0.02)

    # Starup algorithm
    algoInstance = algo.Algorithm(network, (x,y))
    newPosition(x,y)

    counter = 0
    while True:
        algoInstance.step()
        time.sleep(0.01)
        counter += 1
        if counter == 20:
            counter = 0
            algoInstance.getDirection()
            x,y = algoInstance.getNextPosition(algoInstance.facingDirection)
            newPosition(x,y)

if __name__ == "__main__":
    while True:
        try:
            main()
        except AttributeError:
            main() 