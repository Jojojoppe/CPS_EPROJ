class Message():
    def __init__(self):
        self.data = b''
        self.length = 0
        self.done = False
        
    # Create message object from string of bytes
    @classmethod
    def create(cls, data:bytes):
        msg = cls()
        msg.data = data
        msg.length = len(data)
        msg.done = True
        return msg

    # Reconstruct data from received message. Returns Message object and rest of data
    @classmethod
    def recreate(cls, inp:bytes):
        # Must at least receive length field
        if len(inp)<4:
            return None,inp
        # create object
        msg = cls()
        # Get length from message
        blen = int.from_bytes(inp[0:3], byteorder="little")
        msg.length = blen
        if blen>(len(inp)-4):
            # Packet is not done
            msg.data = inp[4:]
            return msg,b''
        msg.data = inp[4:4+blen]
        msg.done = True
        return msg,inp[4+blen:]

    # If packet not yet done, append bytes until it is
    def finish(self, inp:bytes):
        if self.done:
            return inp
        if self.length-len(self.data)>len(inp):
            #still not enough bytes
            self.data += inp
            return b''
        else:
            self.data += inp[:self.length-len(self.data)]
            self.done = True
            return inp[self.length-len(self.data):]
            
    # Create packet from message to be sent
    def packet(self):
        if not self.done:
            return None
        blen = self.length.to_bytes(4, byteorder="little")
        return blen+self.data
    # Stringify message
    def __repr__(self):
        return '%d:%d: %s' % (self.done, self.length, str(self.data))