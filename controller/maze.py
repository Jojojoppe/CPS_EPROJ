import random
import pygame
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
    def __repr__(self):
        return "%d,%d\t%s N:%s E:%s S:%s W:%s"%(self.x, self.y, str(self.visited),
            str(self.north), str(self.east), str(self.south), str(self.west))

"""Maze class

Contains the database of the maze and generator functions
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

if __name__=="__main__":
    m = Maze()
    m.generate()

    gs = 16
    offs = 16

    pygame.init()
    window = pygame.display.set_mode((2*offs+gs*m.width, 2*offs+gs*m.height), 0, 32)
    while True:
        window.fill((255, 255, 255))

        for w in range(m.width):
            for h in range(m.height):
                if m.grid[(w,h)].west:
                    pygame.draw.line(window, (0,0,0), (offs+w*gs, offs+h*gs), (offs+w*gs, offs+(h+1)*gs), 1)
                if m.grid[(w,h)].north:
                    pygame.draw.line(window, (0,0,0), (offs+w*gs, offs+h*gs), (offs+(w+1)*gs, offs+h*gs), 1)
                if m.grid[(w,h)].east:
                    pygame.draw.line(window, (0,0,0), (offs+(w+1)*gs, offs+h*gs), (offs+(w+1)*gs, offs+(h+1)*gs), 1)
                if m.grid[(w,h)].south:
                    pygame.draw.line(window, (0,0,0), (offs+w*gs, offs+(h+1)*gs), (offs+(w+1)*gs, offs+(h+1)*gs), 1)
        
        pygame.display.update()
    pygame.quit()