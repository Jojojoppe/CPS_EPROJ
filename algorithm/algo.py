import enum
import random
import sys
import pickle
import time

import threading
import pygame


NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

STRAIGHT = 0
RIGHT = 1
BACK = 2
LEFT = 3
STOP = 4

TTL = 200

"""Algorithm class
"""


class Algorithm:
    class SolvingStates(enum.Enum):
        EXPLORE = 0
        GOTOMEETINGPOINT = 1
        GOTOOPENPATH = 2
        GOTOEXIT = 3
        GOTORAND = 4

    def gui(self):
        pygame.init()
        fpsCam = pygame.time.Clock()
        gOffs, gGS = 16, 16
        window = pygame.display.set_mode((16 * gGS + 2 * gOffs, 16 * gGS + 2 * gOffs), 0, 32)

        while True:
            window.fill((220, 220, 220))

            # Draw known maze tiles
            for k, v in self.mazeMemory.items():
                x, y = k
                pygame.draw.rect(window, (255, 255, 255), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))

            # Draw known junctions
            for k, v in self.junctions.items():
                x, y = k
                if v:
                    pygame.draw.rect(window, (220, 220, 255), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))
                else:
                    pygame.draw.rect(window, (255, 220, 220), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))

            # Draw meeting point
            x, y = self.meetingPoint
            pygame.draw.rect(window, (0, 255, 0), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))

            # Draw exit if known
            if self.exitFound is not None:
                x,y = self.exitFound
                pygame.draw.rect(window, (255, 255, 0), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))

            if self.nextPosition is not None:
                x,y = self.nextPosition
                pygame.draw.rect(window, (255, 0, 255), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))
            if self.prevPosition is not None:
                x,y = self.prevPosition
                pygame.draw.rect(window, (255, 127, 0), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))

            # If there are other next potitions draw them
            if self.otherNextPositions is not None:
                for k, p in self.otherNextPositions.items():
                    if p is None:
                        continue
                    x, y = p
                    pygame.draw.rect(window, (0, 255, 255), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))
            if self.otherPositions is not None:
                for k, p in self.otherPositions.items():
                    if p is None:
                        continue
                    x, y = p
                    pygame.draw.rect(window, (0, 255, 255), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))


            # Draw route to self
            for k, v in self.routeToSelf.items():
                x, y = k
                px, py = v
                pygame.draw.circle(window, (160, 160, 160),
                                   (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)), 2, 0)
                if px == x and py == y - 1:
                    pygame.draw.line(window, (160, 160, 160),
                                     (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                     (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y) * gGS)), 1)
                elif px == x and py == y + 1:
                    pygame.draw.line(window, (160, 160, 160),
                                     (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                     (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 1) * gGS)), 1)
                elif px == x - 1 and py == y:
                    pygame.draw.line(window, (160, 160, 160),
                                     (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                     (int(gOffs + (x) * gGS), int(gOffs + (y + 0.5) * gGS)), 1)
                elif px == x + 1 and py == y:
                    pygame.draw.line(window, (160, 160, 160),
                                     (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                     (int(gOffs + (x + 1.0) * gGS), int(gOffs + (y + 0.5) * gGS)), 1)

            # Draw target junction if one
            if self.solvingState == self.SolvingStates.GOTOOPENPATH:
                if self.targetJunction != None:
                    x, y = self.targetJunction
                    pygame.draw.circle(window, (0, 0, 255),
                                       (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)), 2, 0)

            # Draw known maze walls
            for k, v in self.mazeMemory.items():
                x, y = k
                north, east, south, west, final = v
                if west:
                    pygame.draw.line(window, (0, 0, 0), (gOffs + x * gGS, gOffs + y * gGS),
                                     (gOffs + x * gGS, gOffs + (y + 1) * gGS), 1)
                if north:
                    pygame.draw.line(window, (0, 0, 0), (gOffs + x * gGS, gOffs + y * gGS),
                                     (gOffs + (x + 1) * gGS, gOffs + y * gGS), 1)
                if east:
                    pygame.draw.line(window, (0, 0, 0), (gOffs + (x + 1) * gGS, gOffs + y * gGS),
                                     (gOffs + (x + 1) * gGS, gOffs + (y + 1) * gGS), 1)
                if south:
                    pygame.draw.line(window, (0, 0, 0), (gOffs + x * gGS, gOffs + (y + 1) * gGS),
                                     (gOffs + (x + 1) * gGS, gOffs + (y + 1) * gGS), 1)

            # Draw current position
            x, y = self.position
            pygame.draw.circle(window, (255, 0, 0), (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)), 2, 0)
            if self.facingDirection == NORTH:
                pygame.draw.line(window, (255, 0, 0), (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                 (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y) * gGS)), 2)
            elif self.facingDirection == SOUTH:
                pygame.draw.line(window, (255, 0, 0), (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                 (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 1) * gGS)), 2)
            elif self.facingDirection == EAST:
                pygame.draw.line(window, (255, 0, 0), (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                 (int(gOffs + (x + 1) * gGS), int(gOffs + (y + 0.5) * gGS)), 2)
            elif self.facingDirection == WEST:
                pygame.draw.line(window, (255, 0, 0), (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                 (int(gOffs + (x) * gGS), int(gOffs + (y + 0.5) * gGS)), 2)

            # Draw other positions
            for k, p in self.otherPositions.items():
                x, y = p
                pygame.draw.circle(window, (0, 0, 0), (int(gOffs + (x + 0.5) * gGS), int(gOffs + (y + 0.5) * gGS)),
                                   2, 0)

            pygame.display.update()
            fpsCam.tick(15)

    """ Init function
    """

    def __init__(self, network, position):
        self.network = network

        self.ID = network.ip + str(network.port)

        self.ignore = False

        self.update = False
        self.sync = False
        self.scount = 0

        # Internal state variables
        self.position = position
        self.justStarted = True
        self.prevPosition = None
        self.nextPosition = None
        self.positionInfo = (False, False, False, False, False)
        self.facingDirection = NORTH
        self.meetingPoint = position

        # Other bots
        self.otherPositions = {}
        self.otherNextPositions = {}
        self.otherPositionTTL = {}

        # Algo parameters
        self.amountInSwarm = 2

        # Map memory
        self.mazeMemory = {}
        self.exitFound = None
        # Route to self map
        self.routeToSelf = {}
        # Open paths (not yet explored)
        self.junctions = {}  # [pt] = (bool explored)
        self.junctions[position] = False
        self.targetJunction = None
        self.possibleNewMeetingPoints = set()

        # Solving state
        self.solvingState = self.SolvingStates.EXPLORE

        # Timer counter
        self.counter = 0

        # Update buffers
        self.updateMazeMemory = []
        self.updateRouteToSelf = []
        self.updatejunctions = []
        self.updateOtherPositions = []
        self.updateOtherNextPositions = []
        self.mayUpdate = False
        self.mayGoToExit = False

        self.guiThread = threading.Thread(target=self.gui)
        self.guiThread.start()


    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['network']
        del state['guiThread']
        return state

    def __setstate__(self, state):
        # Restore instance attributes (i.e., filename and lineno).
        self.__dict__.update(state)
        # Restore the previously opened file's state. To do so, we need to
        # reopen it and read from it until the line count is restored.

    def restoreState(self, network):
        self.network = network
        self.guiThread = threading.Thread(target=self.gui)
        self.guiThread.start()

    # Return if the meeting point is explored
    def checkMeetingPoint(self):
        return self.junctions[self.meetingPoint]

    """ Called when message is received
    Updates internal memory without changing it: pushes to internal buffer which is resolved by step()
    """

    def recv(self, data: bytes, rssi: int):

        self.mayUpdate = False
        msgData = pickle.loads(data)
        otherMazeMemory = msgData[0]
        otherRouteToSelf = msgData[1]
        otherjunctions = msgData[2]
        otherPosition = msgData[3]
        otherID = msgData[4]
        otherMeeting = msgData[5]
        othersync = msgData[6]
        otherExitFound = msgData[7]
        otherNextPosition = msgData[8]

        self.sync = True

        # Update ID
        self.updateOtherPositions.append((otherID,otherPosition))
        self.updateOtherNextPositions.append((otherID,otherNextPosition))

        # Update maze memory
        #print("Updating maze memory")
        for k, v in otherMazeMemory.items():
            if k not in self.mazeMemory:
                self.updateMazeMemory.append((k, v))

        # Update routeToSelf
        # FIXME self.meetingpoint? Not the same as mine?
        # FIXME self on meeting point?
        # Update complete routeToSelf map
        #print("Update routeToSelf")
        for k, v in otherRouteToSelf.items():
            if k not in self.routeToSelf:
                self.updateRouteToSelf.append((k, v))
        # Overwrite path from other to last common point
        route = self.getPathFromPointToPoint(otherRouteToSelf, self.meetingPoint, otherPosition)
        uniqueRoute = []
        notUniqueRoute = []
        # Delete points we already know
        for p in route:
            if p not in self.routeToSelf and p != self.position:
                uniqueRoute.append(p)
            else:
                notUniqueRoute.append(p)
        if len(uniqueRoute) > 0:
            for i in range(len(uniqueRoute) - 1):
                p = uniqueRoute[-1 * i - 1]
                np = uniqueRoute[-1 * i - 2]
                self.updateRouteToSelf.append((p, np))
            p = uniqueRoute[0]
            np = notUniqueRoute[-1]
            self.updateRouteToSelf.append((p, np))

        # Update junctions
        #print("Update junctions")
        for k, v in otherjunctions.items():
            # If new junction
            if k not in self.junctions:
                self.updatejunctions.append((k, v))
            # If known junction of other bot is explored
            elif v and not self.junctions[k]:
                self.updatejunctions.append((k, v))

        if otherExitFound is not None and self.exitFound is not None:
            # BOTH KNOW EXIT
            self.mayGoToExit = True
        
        if otherExitFound is not None:
            self.exitFound = otherExitFound

        self.mayUpdate = True
        #print("Done receiving")

    """[summary]
    """

    def updateFromBuffers(self):
        if not self.mayUpdate:
            return
        self.mayUpdate = False
        # Update maze memory from buffer
        for upd in self.updateMazeMemory:
            self.mazeMemory[upd[0]] = upd[1]
        self.updateMazeMemory.clear()
        # Update route to self from buffer
        for upd in self.updateRouteToSelf:
            self.routeToSelf[upd[0]] = upd[1]
        self.updateRouteToSelf.clear()
        # Update unexplored junctions
        for upd in self.updatejunctions:
            self.junctions[upd[0]] = upd[1]
        self.updatejunctions.clear()

        for upd in self.updateOtherPositions:
            self.otherPositions[upd[0]] = upd[1]
            self.otherPositionTTL[upd[0]] = TTL
        self.updateOtherPositions.clear()
        for upd in self.updateOtherNextPositions:
            self.otherNextPositions[upd[0]] = upd[1]
        self.updateOtherNextPositions.clear()

        if self.mayGoToExit:
            self.solvingState = self.SolvingStates.GOTOEXIT

    """ Called in main loop
    """

    def step(self):
        self.counter += 1

        self.updateFromBuffers()

        # Broadcast maze, routeToSeld and unexploredJunction
        if self.counter % 10 == 0:
            #print("Send a packet")
            self.network.send(pickle.dumps(
                [self.mazeMemory, self.routeToSelf, self.junctions, self.position, self.ID, self.meetingPoint, self.sync, self.exitFound, self.nextPosition]
            ))

        for k,v in self.otherPositionTTL.items():
            if v==0 and k in self.otherPositions:
                self.otherPositions.pop(k)
                self.otherNextPositions.pop(k)
            else:
                self.otherPositionTTL[k] = v-1

    """ Called when aruco marker is detected
    position: (x,y)
    info: (north, east, south, west, final) (ABSOLUTE), True is wall, False is opening
    """

    def newPos(self, position, info):
        print("newPos()", position, self.prevPosition)
        # FIXME next test do not return
        if position == self.position and not self.justStarted:
            print("IGNORING pos:", position, " prevPos:", self.position)
            self.ignore = True
            return
        else:
            self.ignore = False
        self.justStarted = False
        self.prevPosition = self.position  # Save previous position
        self.position = position  # Update position
        self.positionInfo = info
        self.mazeMemory[position] = info
        if info[4]:
            self.exitFound = position
        # Update route to self map
        # Every EDGE (between two points) needs data. problem: 1->2 and 2->1 are same
        # edge, so just adding both combinations to dict will always update the edge
        self.routeToSelf[self.prevPosition] = self.position

    """ Called when new direction is needed
    Returns string: left right straight back (RELATIVE)
    """

    def avgT(self, a, b):
        return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2

    def manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def getDirection(self):

        if self.ignore:
            print("GD: ignored")
            self.ignore = False
            return STRAIGHT

        other = (-1, -1)
        for c in self.otherPositions:
            other = self.otherPositions[c]

        if self.sync:
            avg = self.avgT(self.position, other)
            maxi = (-1, self.meetingPoint)
            if self.checkMeetingPoint():
                for j in self.junctions:
                    if not self.junctions[j]:
                        if self.manhattan(j, avg) > maxi[0]:
                            maxi = (self.manhattan(j, avg), j)
                # print("New meeting point")
            self.meetingPoint = maxi[1]
        self.sync = False

        oldFacingDirection = self.facingDirection
        oldNextPosition = self.nextPosition

        # if self.meetingPoint in self.junctions:
        #     print(self.junctions[self.meetingPoint])
        print("GD: entering while")
        while True:
            print("GD state: ", self.solvingState)

            if self.solvingState == self.SolvingStates.EXPLORE:
                print("EXPLORE")
                self.updateFromBuffers()
                occupied = False  # TODO different source
                newDirection = None
                if self.position in self.junctions:
                    self.junctions[self.position] = True
                # i is relative direction: first look if I can drive straight ahead
                for i in range(4):
                    d = self.Rel2Abs(i)
                    # If no wall in direction, if not occupied, and not aleady visited
                    if not self.positionInfo[d] and not occupied and self.getNextPosition(d) not in self.mazeMemory:
                        if newDirection is None:
                            newDirection = i
                            self.facingDirection = d
                        else:
                            # There are Enexplored open paths starting from this position
                            self.junctions[self.position] = False
                if newDirection is not None:
                    self.nextPosition = self.getNextPosition(self.facingDirection)
                    #return self.mayGoToNextPoint(newDirection)
                    return self.mayGoToNextPoint(newDirection, oldFacingDirection, oldNextPosition)

                # No possible direction
                self.solvingState = self.SolvingStates.GOTOMEETINGPOINT

            if self.solvingState == self.SolvingStates.GOTOMEETINGPOINT:
                print("GOTOMEETINGPOINT")

                newdir = self.getNextDirectionToPoint(self.meetingPoint)
                # for j in self.junctions:
                #     if not self.junctions[j]:
                #         newdir = self.getNextDirectionToPoint(j)


                if newdir is None:
                    self.solvingState = self.SolvingStates.GOTOOPENPATH
                else:
                    relDirection = self.Abs2Rel(newdir)
                    self.facingDirection = newdir
                    self.nextPosition = self.getNextPosition(newdir)
                    print("GoToMeetingPoint return:", newdir)
                    #return self.mayGoToNextPoint(relDirection)
                    return self.mayGoToNextPoint(relDirection, oldFacingDirection, oldNextPosition)

            if self.solvingState == self.SolvingStates.GOTOOPENPATH:
                self.updateFromBuffers()
                # Calculate target junction
                # -> First junction with unexplored open paths
                for jPt, jExplored in self.junctions.items():
                    if not jExplored:
                        self.targetJunction = jPt
                        break
                if self.targetJunction is None:
                    # No unexplored junctions
                    self.nextPosition = self.position
                    return STOP
                else:
                    newdir = self.getNextDirectionToPoint(self.targetJunction)
                    if newdir is None:
                        # TODO ???
                        # Reached destination
                        self.targetJunction = None
                        self.solvingState = self.SolvingStates.EXPLORE
                    else:
                        relDirection = self.Abs2Rel(newdir)
                        self.facingDirection = newdir
                        self.nextPosition = self.getNextPosition(newdir)
                        print("GotoOpenPath return:", newdir, relDirection)
                        #return self.mayGoToNextPoint(relDirection)
                        return self.mayGoToNextPoint(relDirection, oldFacingDirection, oldNextPosition)

            if self.solvingState == self.SolvingStates.GOTOEXIT:
                print("GOTOEXIT")
                self.updateFromBuffers()
                newdir = self.getNextDirectionToPoint(self.exitFound)
                if newdir is None:
                    # TODO ???
                    # Reached destination
                    self.nextPosition = self.position
                    return STOP
                else:
                    relDirection = self.Abs2Rel(newdir)
                    self.facingDirection = newdir
                    self.nextPosition = self.getNextPosition(newdir)
                    print("GotoExit return:", newdir)
                    #return self.mayGoToNextPoint(relDirection)
                    return self.mayGoToNextPoint(relDirection, oldFacingDirection, oldNextPosition)

            if self.solvingState == self.SolvingStates.GOTORAND:
                print("GOTORAND")
                self.updateFromBuffers()
                pt = list(self.junctions.keys())[random.randint(0, len(self.junctions)-1)]
                print("Trying point ", pt)
                newdir = self.getNextDirectionToPoint(pt)
                if newdir is None:
                    # TODO ???
                    # Reached destination
                    self.nextPosition = self.position
                    return STOP
                else:
                    relDirection = self.Abs2Rel(newdir)
                    self.facingDirection = newdir
                    self.nextPosition = self.getNextPosition(newdir)
                    self.solvingState = self.SolvingStates.EXPLORE
                    retval = self.mayGoToNextPoint(relDirection, oldFacingDirection, oldNextPosition)
                    return retval

            time.sleep(0)

    """ Convert absolute direction to relative
    Returns relative direction
    """

    def Abs2Rel(self, newdir):
        #d = newdir - self.facingDirection
        #while d>4:
        #    d -= 4
        #while d<0:
        #    d += 4
        return (newdir - self.facingDirection) % 4
        #return d

    """Convert relative direction to absolute
    Returns absolute direction
    """

    def Rel2Abs(self, newdir):
        return (newdir + self.facingDirection) % 4

    """ Get next position of adjacent square in a certain direction
    Dir->Pos
    """

    def getNextPosition(self, newDir):
        x, y = self.position
        if newDir == NORTH:
            return x, y - 1
        elif newDir == EAST:
            return x + 1, y
        elif newDir == SOUTH:
            return x, y + 1
        elif newDir == WEST:
            return x - 1, y
        else:
            raise ValueError

    """ Get corresponding direction from current position to a adjacent position
    Pos->Dir
    """

    def getNextDirection(self, newPos):
        nx, ny = newPos
        x, y = self.position
        if nx == x and ny == y - 1:
            return NORTH
        elif nx == x + 1 and ny == y:
            return EAST
        elif nx == x and ny == y + 1:
            return SOUTH
        elif nx == x - 1 and ny == y:
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
        if pt not in self.routeToSelf:
            return None
        while pt != self.position:
            if pt in self.routeToSelf:
                routeFromPoint.append(self.routeToSelf[pt])
                pt = self.routeToSelf[pt]
        # Check if at the meeting point
        if len(routeFromPoint) == 1:
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
        while pt != ptTo:
            if pt in routeToSelf:
                routeFromPoint.append(routeToSelf[pt])
                pt = routeToSelf[pt]

        return routeFromPoint


    def mayGoToNextPoint(self, newDir, oldFacingDirection, oldNextPosition):
        print("MayGoToNextPoint(", newDir, ")")
        print(" > ", self.otherPositions)
        for k,v in self.otherPositions.items():
            if self.nextPosition == v:
                self.solvingState = self.SolvingStates.GOTORAND
                self.facingDirection = oldFacingDirection
                self.nextPosition = oldNextPosition
                return STOP
        print(" > ", self.otherNextPositions)
        for k,v in self.otherNextPositions.items():
            if self.nextPosition == v:
                self.solvingState = self.SolvingStates.GOTORAND
                self.facingDirection = oldFacingDirection
                self.nextPosition = oldNextPosition
                return STOP
        return newDir

if __name__ == "__main__":
    pass

# Notes:
# initial prevPosition may be None if bot starts on a position and NOT outside the maze
# Assumption for now: starting next to eachother and 2 bots in swarm
# 0,0 is left upper corner (like in images)

# 4 MAIN FUNCIONS
# recv: receive message callback
# step: callback called in control loop
# newPos: called when aruco marker is scanned
# getDirection: directly called after newPos() to get relative direction to drive in
