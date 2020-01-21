import enum
import random
#from NetworkEmulator.netemuclient import NetEmuClient

class AbsoluteDirection(enum.Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class RelativeDirection(enum.Enum):
    STRAIGHT = 0
    RIGHT = 1
    BACK = 2
    LEFT = 3

"""Algorithm class
"""
class Algorithm():
    """ Init function
    """
    def __init__(self, network, position):
        self.network = network

        # Internal state variables
        self.position = position
        self.prevPosition = None
        self.positionInfo = (False, False, False, False, False)
        self.facingDirection = AbsoluteDirection.NORTH

        # Map memory
        self.mazeMemory = {}
        # Route to self map
        self.routeToSelf = {}

    """ Called when message is received
    """
    def recv(self, data:bytes, rssi:int):
        pass

    """ Called in main loop
    """
    def step(self):
        pass

    """ Called when aruco marker is detected
    position: (x,y)
    info: (north, east, south, west, final) (ABSOLUTE), True is wall, False is opening
    """
    def newPos(self, position, info):
        self.prevPosition = self.position       # Save previous position
        self.position = position                # Update position
        self.positionInfo = info
        self.mazeMemory[position] = info
        # Update route to self map
        # Every EDGE (between two points) needs data. problem: 1->2 and 2->1 are same
        # edge, so just adding both combinations to dict will always update the edge
        self.routeToSelf[(self.prevPosition, self.position)] = self.position
        self.routeToSelf[(self.position, self.prevPosition)] = self.position
        

    """ Called when new direction is needed
    Returns string: left right straight back (RELATIVE)
    """
    def getDirection(self):
        # Return random possible direction
        possible = []
        for i in range(4):
            if not self.positionInfo[i]:
                possible.append(i)
        newdir = self.Abs2Rel(possible[random.randint(0, len(possible)-1)])
        self.facingDirection = newdir
        return newdir

    """ Convert absolute direction to relative
    Returns relative direction
    """
    def Abs2Rel(self, newdir:AbsoluteDirection):
        return (newdir-self.facingDirection)%4

    """Convert relative direction to absolute
    Returns absolute direction
    """
    def Rel2Abs(self, newdir:RelativeDirection):
        return (newdir+self.facingDirection)%4

if __name__ == "__main__":
    pass

# Notes:
# initial prevPosition may be None if bot starts on a position and NOT outside the maze