class Space:

    def __init__(self):
        self.markers = {}
    

    def get_marker(ID):

        if ID in self.markers:
            return self.markers[ID]
        else:
            raise ValueError

    def register_marker(ID, turns):
        self.markers[ID] = turns


    def get_all_markers():
        return self.markers


class Direction:

    dirs = ["N", "E", "S", "W"]

    def __init__(self):
        self.direction = "N"

    def turn_c(self, d):        
        i = self.dirs.index(self.direction)

        if d == "left":
            i -= 1
        elif d == "right":
            i += 1
        elif d == "around":
            i += 2
        else:
            raise ValueError

        i = i % 4
        self.direction = self.dirs[i]

    def get_direction(self):
        return self.direction
        