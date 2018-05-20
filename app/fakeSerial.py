# fakeSerial.py
# D. Thiebaut
# A very crude simulator for PySerial assuming it
# is emulating an Arduino.


# a Serial class emulator
class Serial:

    ## init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
    def __init__( self, port='COM1', baudrate = 19200, timeout=1,
                  bytesize = 8, parity = 'N', stopbits = 1, xonxoff=0,
                  rtscts = 0):
        self.name     = port
        self.port     = port
        self.timeout  = timeout
        self.parity   = parity
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self._isOpen  = True
        self._receivedData = []
        self.cmd = 0x00
        self._data = []

    ## isOpen()
    # returns True if the port to the Arduino is open.  False otherwise
    def isOpen( self ):
        return self._isOpen

    ## open()
    # opens the port
    def open( self ):
        self._isOpen = True

    ## close()
    # closes the port
    def close( self ):
        self._isOpen = False

    ## write()
    # writes a string of characters to the Arduino
    def populate(self):
        self._data.extend([0x11,0xAB,0xCD,0x0a])
        self._data.extend([0x11,0x2,0x0a])


    def write( self, string ):
        print( 'Arduino got: "' + ":".join(hex(int(c)) for c in string) + '"' )
        self.cmd = int(string[0])
        print(self.cmd)
        self._receivedData.append(string)
        if self.cmd == 0x01:
            self._data.extend([0x01,0x00,0x01,0x01,0x01,0x01,0x01,0x0a])
        elif self.cmd == 0x10:
            self._data.extend([0x10,0x02,0x0a])
            self._data.extend([0x02,0xEF,0xCD,0x0a])
            self._data.extend([0x03,0x12,0x12,0x0a])
            self._data.extend([0x10,0x0a])

        print(self._data)

    ## read()
    # reads n characters from the fake Arduino. Actually n characters
    # are read from the string _data and returned to the caller.
    def read( self, n=1 ):
        s = self._data[0:n]
        self._data = self._data[n:]
        #print( "read: now self._data = ", self._data )
        return s

    ## readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline( self ):
        if len(self._data) <= 0:
            return []
        index = self._data.index(0x0a)

        if index != -1:
            resp = self._data[0:index]
            self._data = self._data[index+1:]
            return resp
        else:
            return []

    ## __str__()
    # returns a string representation of the serial class
    def __str__( self ):
        return  "Serial<id=0xa81c10, open=%s>( port='%s', baudrate=%d," \
               % ( str(self.isOpen), self.port, self.baudrate ) \
               + " bytesize=%d, parity='%s', stopbits=%d, xonxoff=%d, rtscts=%d)"\
               % ( self.bytesize, self.parity, self.stopbits, self.xonxoff,
                   self.rtscts )
