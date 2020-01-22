import enum
import random
import sys
import pickle
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

        # Timer counter
        self.counter = 0

        # Update buffers
        self.updateMazeMemory = []
        self.updateRouteToSelf = []

    """ Called when message is received
    Updates internal memory without changing it: pushes to internal buffer which is resolved by step()
    """
    def recv(self, data:bytes, rssi:int):
        msgData = pickle.loads(data)
        otherMazeMemory = msgData[0]
        otherRouteToSelf = msgData[1]
        otherUnexploredJunctions = msgData[2]
        otherPosition = msgData[3]

        # Update maze memory
        for k,v in otherMazeMemory.items():
            if k not in self.mazeMemory:
                self.updateMazeMemory.append((k,v))

        # Update route to self
        # for k,v in otherRouteToSelf.items():
        #     if k not in self.routeToSelf:
        #         self.updateRouteToSelf.append((k,v))
        # FIXME self.meetingpoint? Not the same as mine?
        route = self.getPathFromPointToPoint(otherRouteToSelf, self.meetingPoint, otherPosition)
        print()
        print(route)
        uniqueRoute = []
        notUniqueRoute = []
        # Delete points we already know
        for p in route:
            if p not in self.routeToSelf and p!=self.position:
                uniqueRoute.append(p)
            else:
                notUniqueRoute.append(p)
        print(uniqueRoute)
        print(notUniqueRoute)
        if len(uniqueRoute)>0:
            for i in range(len(uniqueRoute)-1):
                p = uniqueRoute[-1*i-1]
                np = uniqueRoute[-1*i-2]
                self.updateRouteToSelf.append((p, np))
            p = uniqueRoute[0]
            np = notUniqueRoute[-1]
            self.updateRouteToSelf.append((p, np))
            print(self.updateRouteToSelf)

    """[summary]
    """
    def updateFromBuffers(self):
        # Update maze memory from buffer
        for upd in self.updateMazeMemory:
            self.mazeMemory[upd[0]] = upd[1]
        self.updateMazeMemory.clear()
        # Update route to self from buffer
        for upd in self.updateRouteToSelf:
            self.routeToSelf[upd[0]] = upd[1]
        self.updateRouteToSelf.clear()

    """ Called in main loop
    """
    def step(self):
        self.counter += 1

        self.updateFromBuffers()

        # Broadcast maze, routeToSeld and unexploredJunction
        if self.counter%5==0:
            self.network.send(pickle.dumps(
                [self.mazeMemory, self.routeToSelf, self.unexploredJunctions, self.position]
            ))

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
        while pt!=self.position:
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

    """ Get path from position to a specific known point in
    the maze.
    Gets this info from routeToSelf
    pt's: (x,y)
    Returns: route from point to point
    """
    def getPathFromPointToPoint(self, routeToSelf, ptFrom, ptTo):
        pt = ptFrom
        routeFromPoint = [ptFrom]
        while pt!=ptTo:
            if pt in routeToSelf:
                routeFromPoint.append(routeToSelf[pt])
                pt = routeToSelf[pt]

        return routeFromPoint

if __name__ == "__main__":
    pass

# Notes:
# initial prevPosition may be None if bot starts on a position and NOT outside the maze
# Assumption for now: starting next to eachother and 2 bots in swarm
# 0,0 is left upper corner (like in images)