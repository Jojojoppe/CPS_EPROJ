from NetworkEmulator.netemuclient import NetEmuClient

class Algorithm():
    def __init__(self, network:NetEmuClient):
        self.network = network

    def recv(self, data:bytes, rssi:int):
        pass