import random
import pickle
# import pygame
from enum import Enum

class Cell():
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y
        self.visited = False
        self.north = True
        self.east = True
        self.south = True
        self.west = True
        self.final = False
    def __repr__(self):
        return "%d,%d\t%s N:%s E:%s S:%s W:%s"%(self.x, self.y, str(self.visited),
            str(self.north), str(self.east), str(self.south), str(self.west))

"""Maze class

Contains the database of the mgit@github.com:Jojojoppe/CPS_EPROJ.gitaze and generator functions
"""
class Maze():
    def __init__(self, w=16, h=16):
        self.width = w
        self.height = h
        self.initial = (0, 0)

        self.grid = {}
        for h in range(self.height):
            for w in range(self.width):
                self.grid[(w,h)] = Cell(w, h)

    def generate(self):
        stack = []
        self.grid[self.initial].visited = True
        stack.append(self.initial)
        while len(stack)>0:
            current = stack.pop()
            neighbours = self.get_neighbours(self.grid[current])
            if len(neighbours)>0:
                stack.append(current)
                r = random.randint(0, len(neighbours)-1)
                chosen = neighbours[r]
                # Remove wall between
                if self.grid[current].x == self.grid[chosen].x:
                    if self.grid[current].y > self.grid[chosen].y:
                        self.grid[current].north = False
                        self.grid[chosen].south = False
                    else:
                        self.grid[current].south = False
                        self.grid[chosen].north = False
                elif self.grid[current].y == self.grid[chosen].y:
                    if self.grid[current].x > self.grid[chosen].x:
                        self.grid[current].west = False
                        self.grid[chosen].east = False
                    else:
                        self.grid[current].east = False
                        self.grid[chosen].west = False
                self.grid[chosen].visited = True
                stack.append(chosen)
        # Generate random endpoint
        side = random.randint(0,3)
        # North
        if side==0:
            nr = random.randint(0,self.width-1)
            self.grid[(nr, 0)].north = False
            self.grid[(nr, 0)].final = True
        # South
        elif side==1:
            nr = random.randint(0,self.width-1)
            self.grid[(nr, self.height-1)].south = False
            self.grid[(nr, self.height-1)].final = True
        # East
        elif side==2:
            nr = random.randint(0,self.height-1)
            self.grid[(self.width-1, nr)].east = False
            self.grid[(self.width-1, nr)].final = True
        # West
        elif side==3:
            nr = random.randint(0,self.height-1)
            self.grid[(0, nr)].west = False
            self.grid[(0, nr)].final = True

    def get_neighbours(self, c:Cell):
        res = []
        if (c.x+1,c.y) in self.grid and not self.grid[(c.x+1,c.y)].visited: res.append((c.x+1, c.y))
        if (c.x-1,c.y) in self.grid and not self.grid[(c.x-1,c.y)].visited: res.append((c.x-1, c.y))
        if (c.x,c.y+1) in self.grid and not self.grid[(c.x,c.y+1)].visited: res.append((c.x, c.y+1))
        if (c.x,c.y-1) in self.grid and not self.grid[(c.x,c.y-1)].visited: res.append((c.x, c.y-1))
        return res

    def print_grid(self):
        for h in range(self.height):
            for w in range(self.width):
                print(self.grid[(w,h)])
            
    @classmethod
    def load(cls, path):
        f = open(path, "rb")
        maze = pickle.loads(f.read())
        f.close()
        return maze

    def save(self, path):
        f = open(path, "wb")
        f.write(pickle.dumps(self))
        f.close()

    def dumps(self):
        return pickle.dumps(self)

    @classmethod
    def loads(cls, data:bytes):
        return pickle.loads(data)

    """Get info of position
    Returns tupe with:
        north, east, south, west: True if wall, False if open
        final: True if exit of maze
    """
    def getInfo(self, pos):
        c = self.grid[pos]
        return c.north, c.east, c.south, c.west, c.final