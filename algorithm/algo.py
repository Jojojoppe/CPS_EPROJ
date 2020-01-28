import enum
import random
import sys
import pickle
import time

import threading
import pygame

# Constants for absolute direction
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

# Constants for relative direction
STRAIGHT = 0
RIGHT = 1
BACK = 2
LEFT = 3
STOP = 4

# Time to live for position of other bots
# Stored position gets removed after TTL amount
# of iterations
TTL = 200

"""Algorithm class
"""
class Algorithm:

    # Different states of the algorithm
    class SolvingStates(enum.Enum):
        EXPLORE = 0             # Exploring state   
        GOTOMEETINGPOINT = 1    # Going back to meeting point
        GOTOOPENPATH = 2        # Go to a junction with unexplored paths
        GOTOEXIT = 3            # Drive towards the exit
        GOTORAND = 4            # Collision: drive to a random junction for one move and try again

    """ Debug GUI
    Shows the internal memory of the algorithm
    """
    def gui(self):
        pygame.init()
        fpsCam = pygame.time.Clock()
        gOffs, gGS = 16, 16
        window = pygame.display.set_mode((16 * gGS + 2 * gOffs, 16 * gGS + 2 * gOffs), 0, 32)

        # Gui loop
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

            # Draw next position
            if self.nextPosition is not None:
                x,y = self.nextPosition
                pygame.draw.rect(window, (255, 0, 255), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))
            # Draw previous position
            if self.prevPosition is not None:
                x,y = self.prevPosition
                pygame.draw.rect(window, (255, 127, 0), (gOffs + x * gGS, gOffs + y * gGS, gGS, gGS))

            # If there are other's (next) potitions draw them
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
    Sets up algorithm
    [network] reference to network layer
    [position] starting position
    """
    def __init__(self, network, position):
        self.network = network
        self.ID = network.ip + str(network.port)        # ID is needed for other cars to store data
        self.ignore = False                             # Markers may only be read once: ignore is set to True if a marker is read again
        self.update = False
        self.sync = False
        self.scount = 0
        self.position = position
        self.justStarted = True                         # It may only ignore markers when already driving, this prevents ignoring the first marker read
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
        # At each algorithm tick (step()) the buffers are written to the internal state memory
        self.updateMazeMemory = []
        self.updateRouteToSelf = []
        self.updatejunctions = []
        self.updateOtherPositions = []
        self.updateOtherNextPositions = []
        self.mayUpdate = False                      # After receiving data the buffers may be updated
        self.mayGoToExit = False                    # May only go to exit if synced with another bot

        # Start the gui thread
        self.guiThread = threading.Thread(target=self.gui)
        self.guiThread.start()

    """ Get object state
    Used by pickle to pickle the object. The algo object
    contains the network and a thread which are not serializable
    so they must be deleted from the state before pickling
    """
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['network']
        del state['guiThread']
        return state

    """ Set the object state
    Used by pickle to store a pickled object. It sets the stored state
    """
    def __setstate__(self, state):
        self.__dict__.update(state)

    """ Restart the algorithm
    After unpickling the algorithm object the network must be set again
    and the gui thread should be started
    """
    def restoreState(self, network):
        self.network = network
        self.guiThread = threading.Thread(target=self.gui)
        self.guiThread.start()

    """ Return true if the meeting point is explored
    """
    def checkMeetingPoint(self):
        return self.junctions[self.meetingPoint]

    """ Called when message is received
    Updates internal memory without changing it: pushes to internal buffer which is resolved by step()
    """
    def recv(self, data: bytes, rssi: int):
        # Get all data from the packet
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
        # Update complete routeToSelf map
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
        # If there is a unique route use it to update routeToSelf
        if len(uniqueRoute) > 0:
            for i in range(len(uniqueRoute) - 1):
                p = uniqueRoute[-1 * i - 1]
                np = uniqueRoute[-1 * i - 2]
                self.updateRouteToSelf.append((p, np))
            p = uniqueRoute[0]
            np = notUniqueRoute[-1]
            self.updateRouteToSelf.append((p, np))

        # Update junctions
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

    """ Update the internal state memory from the buffers
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
        # Update the other (next) positions
        for upd in self.updateOtherPositions:
            self.otherPositions[upd[0]] = upd[1]
            self.otherPositionTTL[upd[0]] = TTL          # Reset the TTL
        self.updateOtherPositions.clear()
        for upd in self.updateOtherNextPositions:
            self.otherNextPositions[upd[0]] = upd[1]
        self.updateOtherNextPositions.clear()

        if self.mayGoToExit:
            self.solvingState = self.SolvingStates.GOTOEXIT

    """ Algorithm step
    Called in main loop
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

        # Decrease TTL of other positions
        for k,v in self.otherPositionTTL.items():
            if v==0 and k in self.otherPositions:
                self.otherPositions.pop(k)
                self.otherNextPositions.pop(k)
            else:
                self.otherPositionTTL[k] = v-1

    """ Called when aruco marker is detected
    [position] new position in format (x,y)
    [info] detected position information in format (north, east, south, west, final) (ABSOLUTE), True is wall, False is opening
    """
    def newPos(self, position, info):
        # Check if marker is read twice
        if position == self.position and not self.justStarted:
            self.ignore = True
            return
        else:
            self.ignore = False
        self.justStarted = False            # Now not started anymore
        self.prevPosition = self.position   # Save previous position
        self.position = position            # Update position
        self.positionInfo = info
        self.mazeMemory[position] = info
        if info[4]:
            self.exitFound = position
        # Update route to self map
        # Every EDGE (between two points) needs data. problem: 1->2 and 2->1 are same
        # edge, so just adding both combinations to dict will always update the edge
        self.routeToSelf[self.prevPosition] = self.position

    """ Average two positions
    """
    def avgT(self, a, b):
        return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2

    """ Calculate manhattan distance between two points
    """
    def manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    """ Called when new direction is needed
    Returns relative direction: left right straight back stop
    """
    def getDirection(self):
        # Check if must ignore
        if self.ignore:
            self.ignore = False
            return STRAIGHT

        # Decides the new meetingpoint which is the farthest away from the two cars
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
            self.meetingPoint = maxi[1]
        self.sync = False

        # Saving old state in case of collision
        oldFacingDirection = self.facingDirection
        oldNextPosition = self.nextPosition

        # Repeating this until a feasable direction is found
        while True:

            # EXPLORING STATE
            if self.solvingState == self.SolvingStates.EXPLORE:
                self.updateFromBuffers()                        # Check if there are new messages received
                newDirection = None
                # If new position is a junction, set to discovered for now
                if self.position in self.junctions:
                    self.junctions[self.position] = True
                # i is relative direction: first look if I can drive straight ahead
                for i in range(4):
                    d = self.Rel2Abs(i)
                    # If no wall in direction, if not occupied, and not aleady visited
                    if not self.positionInfo[d] and self.getNextPosition(d) not in self.mazeMemory:
                        if newDirection is None:
                            newDirection = i
                            self.facingDirection = d
                        else:
                            # There are Enexplored open paths starting from this position
                            self.junctions[self.position] = False
                # If there is a new direction
                if newDirection is not None:
                    self.nextPosition = self.getNextPosition(self.facingDirection)
                    return self.mayGoToNextPoint(newDirection, oldFacingDirection, oldNextPosition)
                # No possible direction
                self.solvingState = self.SolvingStates.GOTOMEETINGPOINT

            # GOTO MEETING POINT STATE
            if self.solvingState == self.SolvingStates.GOTOMEETINGPOINT:
                # Get direction to meetingpoint
                newdir = self.getNextDirectionToPoint(self.meetingPoint)
                # If there is none
                if newdir is None:
                    self.solvingState = self.SolvingStates.GOTOOPENPATH
                else:
                    relDirection = self.Abs2Rel(newdir)
                    self.facingDirection = newdir
                    self.nextPosition = self.getNextPosition(newdir)
                    return self.mayGoToNextPoint(relDirection, oldFacingDirection, oldNextPosition)

            # GOTO OPEN PATH STATE
            if self.solvingState == self.SolvingStates.GOTOOPENPATH:
                self.updateFromBuffers()
                # Pick a junction to go to
                for jPt, jExplored in self.junctions.items():
                    if not jExplored:
                        self.targetJunction = jPt
                        break
                # If there are no unexplored junctions wait for new information
                if self.targetJunction is None:
                    # No unexplored junctions
                    self.nextPosition = self.position
                    return STOP
                else:
                    # Get direction towards junction
                    newdir = self.getNextDirectionToPoint(self.targetJunction)
                    if newdir is None:
                        # Reached destination
                        self.targetJunction = None
                        self.solvingState = self.SolvingStates.EXPLORE
                    else:
                        relDirection = self.Abs2Rel(newdir)
                        self.facingDirection = newdir
                        self.nextPosition = self.getNextPosition(newdir)
                        return self.mayGoToNextPoint(relDirection, oldFacingDirection, oldNextPosition)

            # GOTO EXIT STATE
            if self.solvingState == self.SolvingStates.GOTOEXIT:
                self.updateFromBuffers()
                newdir = self.getNextDirectionToPoint(self.exitFound)
                if newdir is None:
                    # Reached destination
                    self.nextPosition = self.position
                    return STOP
                else:
                    relDirection = self.Abs2Rel(newdir)
                    self.facingDirection = newdir
                    self.nextPosition = self.getNextPosition(newdir)
                    return self.mayGoToNextPoint(relDirection, oldFacingDirection, oldNextPosition)

            # GOTO RANDOM STATE: collision occured
            if self.solvingState == self.SolvingStates.GOTORAND:
                self.updateFromBuffers()
                # Get a random junction
                pt = list(self.junctions.keys())[random.randint(0, len(self.junctions)-1)]
                newdir = self.getNextDirectionToPoint(pt)
                if newdir is None:
                    # Reached destination
                    self.nextPosition = self.position
                    return STOP
                else:
                    relDirection = self.Abs2Rel(newdir)
                    self.facingDirection = newdir
                    self.nextPosition = self.getNextPosition(newdir)
                    self.solvingState = self.SolvingStates.EXPLORE
                    return self.mayGoToNextPoint(relDirection, oldFacingDirection, oldNextPosition)

            # Give other threads a possibility to go
            time.sleep(0)

    """ Convert absolute direction to relative
    Returns relative direction
    """
    def Abs2Rel(self, newdir):
        return (newdir - self.facingDirection) % 4

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

    """ Check for collision
    Will stop the car if it is a collision and next round will bring the car
    into the GOTORAND state
    """
    def mayGoToNextPoint(self, newDir, oldFacingDirection, oldNextPosition):
        for k,v in self.otherPositions.items():
            if self.nextPosition == v:
                self.solvingState = self.SolvingStates.GOTORAND
                self.facingDirection = oldFacingDirection
                self.nextPosition = oldNextPosition
                return STOP
        for k,v in self.otherNextPositions.items():
            if self.nextPosition == v:
                self.solvingState = self.SolvingStates.GOTORAND
                self.facingDirection = oldFacingDirection
                self.nextPosition = oldNextPosition
                return STOP
        return newDir

if __name__ == "__main__":
    pass