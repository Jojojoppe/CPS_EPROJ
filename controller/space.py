class Space():

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