import enum
import random
import sys
#from NetworkEmulator.netemuclient import NetEmuClient

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

STRAIGHT = 0
RIGHT = 1
BACK = 2
LEFT = 3

"""Algorithm class
"""
class Algorithm():

    class SolvingStates(enum.Enum):
        EXPLORE = 0
        GOTOMEETINGPOINT = 1
        GOTOOPENPATH = 2

    """ Init function
    """
    def __init__(self, network, position):
        self.network = network

        # Internal state variables
        self.position = position
        self.prevPosition = None
        self.positionInfo = (False, False, False, False, False)
        self.facingDirection = NORTH
        self.meetingPoint = position

        # Algo parameters
        self.amountInSwarm = 2

        # Map memory
        self.mazeMemory = {}
        # Route to self map
        self.routeToSelf = {}
        # Open paths (not yet explored)
        self.unexploredJunctions = {}     # [pt] = (bool explored)
        self.targetJunction = None

        # Solving state
        self.solvingState = self.SolvingStates.EXPLORE

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
        self.routeToSelf[self.prevPosition] = self.position
        

    """ Called when new direction is needed
    Returns string: left right straight back (RELATIVE)
    """
    def getDirection(self):
        while True:
            if self.solvingState == self.SolvingStates.EXPLORE:
                occupied = False        # TODO different source
                newDirection = None
                if self.position in self.unexploredJunctions:
                    self.unexploredJunctions[self.position] = True
                # i is relative direction: first look if I can drive straight ahead
                for i in range(4):
                    d = self.Rel2Abs(i)
                    # If no wall in direction, if not occupied, and not aleady visited
                    if not self.positionInfo[d] and not occupied and self.getNextPosition(d) not in self.mazeMemory:
                        if newDirection==None:
                            newDirection = i
                            self.facingDirection = d
                        else:
                            # There are Enexplored open paths starting from this position
                            self.unexploredJunctions[self.position] = False
                            print(self.unexploredJunctions)
                if newDirection!=None:
                    return newDirection

                # No possible direction
                self.solvingState = self.SolvingStates.GOTOMEETINGPOINT

            if self.solvingState == self.SolvingStates.GOTOMEETINGPOINT:
                    newdir = self.getNextDirectionToPoint(self.meetingPoint)
                    if newdir == None:
                        self.solvingState = self.SolvingStates.GOTOOPENPATH
                    else:
                        self.facingDirection = newdir
                        return self.Abs2Rel(newdir)

            if self.solvingState == self.SolvingStates.GOTOOPENPATH:
                # Calculate target junction
                # -> First junction with unexplored open paths
                for jPt, jExplored in self.unexploredJunctions.items():
                    if not jExplored:
                        self.targetJunction = jPt
                        break
                if self.targetJunction == None:
                    # No unexplored junctions
                    # FIXME
                    sys.exit(0)
                newdir = self.getNextDirectionToPoint(self.targetJunction)
                if newdir == None:
                    # TODO ???
                    # Reached destination
                    self.targetJunction = None
                    self.solvingState = self.SolvingStates.EXPLORE
                else:
                    self.facingDirection = newdir
                    return self.Abs2Rel(newdir)

 

    """ Convert absolute direction to relative
    Returns relative direction
    """
    def Abs2Rel(self, newdir):
        return (newdir-self.facingDirection)%4

    """Convert relative direction to absolute
    Returns absolute direction
    """
    def Rel2Abs(self, newdir):
        return (newdir+self.facingDirection)%4

    """ Get next position of adjacent square in a certain direction
    Dir->Pos
    """
    def getNextPosition(self, newDir):
        x, y = self.position
        if newDir == NORTH:
            return x,y-1
        elif newDir == EAST:
            return x+1,y
        elif newDir == SOUTH:
            return x,y+1
        elif newDir == WEST:
            return x-1, y
        else:
            raise ValueError

    """ Get corresponding direction from current position to a adjacent position
    Pos->Dir
    """
    def getNextDirection(self, newPos):
        nx,ny = newPos
        x,y = self.position
        if nx==x and ny==y-1:
            return NORTH
        elif nx==x+1 and ny==y:
            return EAST
        elif nx==x and ny==y+1:
            return SOUTH
        elif nx==x-1 and ny==y:
            return WEST
        else:
            raise ValueError

    """ Get direction to next position to a specific known point in
    the maze.
    Gets this info from routeToSelf
    pt: (x,y)
    Returns: absolute direction towards next square. None if target point reached
    """
    def getNextDirectionToPoint(self, pt):
        routeFromPoint = [pt]
        while True:
            if pt == self.position:
                break

            if pt in self.routeToSelf:
                routeFromPoint.append(self.routeToSelf[pt])
                pt = self.routeToSelf[pt]

        # Check if at the meeting point
        if len(routeFromPoint)==1:
            return None

        else:
            # Found route from meeting point to me
            nextPos = routeFromPoint[-2]
            # Next position is routeToMeetingPoint[1]
            newdir = self.getNextDirection(nextPos)
            return newdir

if __name__ == "__main__":
    pass

# Notes:
# initial prevPosition may be None if bot starts on a position and NOT outside the maze
# Assumption for now: starting next to eachother and 2 bots in swarm
# 0,0 is left upper corner (like in images)