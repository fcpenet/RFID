import serial
#import fakeSerial
import threading
from time import sleep
class SerialManager:
    """
        All outgoing packets must end with \n

        0x00 - initiate whole system turns on everything - returns none
            [0] - 00
            [1] - Serial1 role  00 - Checkout, 01 - Scan
            [2] - Serial2 role
            [3] - Serial3 role

        0x01 - get system states returns the following response:

            [0] - 01
            [1] - Serial1 Role  [0/1] checkout/scan
            [2] - Serial1 State [1/0] on/off
            [3] - Serial2 Role
            [4] - Serial2 State [1/0] on/off
            [5] - Serial3 Role
            [6] - Serial3 State [1/0] on/off

        0x10 - scan for tags, multiple readline is required. returns the following response:
            1st readline:

            [0]     - 10
            [1][2]  - number of tags detected

            succeeding readlines:
            [0] - source serial
            [1] to [END] - EPC

            response ends when [0] - 10 is received, length = 1


        0x11 - checkout received

            [0] - 11
            [1] - serial to set
            [2] - state

    """
    def __init__(self, params, cbScan, cbCheckout):
        self.serial1 = params.serial1
        self.serial2 = params.serial2
        self.serial3 = params.serial3
        self._data = []

        self.cbScan = cbScan
        self.cbCheckout = cbCheckout
        self._coStarted = False;
        try:
            print(params.baud_rate)
            self.serial = serial.Serial(port=params.port_name, baudrate=params.baud_rate, timeout=30)
            thread = threading.Thread(target=self.nonblockingread);
            thread.start()
           # self.serial = fakeSerial.Serial(params.port_name, params.baud_rate)
        except Exception as e:
            raise e


    def initializeSystem(self):
        print('Initializing system...')
        packets = list()
        packets.append(0x00)
        packets.append(int(self.serial1['role']))
        packets.append(int(self.serial2['role']))
        packets.append(int(self.serial3['role']))
        packets.append(0x0A)
        self.serial.write(bytes(packets))
        print('Done.')

    def nonblockingread(self):
        while True:
            print('Waiting...')
            resp = self.serial.readline()
            resp = [x for x in resp[:len(resp)-1]]
            #check tag of resp
            #if 10 scan if 11 checkout
            print('X: ', resp)
            #print(':'.join('{:02x}'.format(t,2) for t in resp))
            if (len(resp) > 0):
                self._data.extend(resp)
                if(resp[0] == 0x10):
                    #call cbScan
                    tags = self.processScan()
                    print('tags', tags)
                    self.cbScan(tags)
                elif(resp[0] == 0x11):
                    #call cbCheckout
                    tags = self.processCheckout()
                    print('tags', tags)
                    self.cbCheckout(tags)
            else:
                #return empty list
                self.cbScan([])

    def close(self):
        self.serial.close()


    def grouped(self, iterable, n):
        "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
        return zip(*[iter(iterable)]*n)


    def scan(self, cb):
        packets = bytes([0x10, 0x0A]) # scan
        self.serial.write(packets)

    def processScan(self):
        return self.getTags(0x10, 0xa0)


    def getTags(self, startByte, endByte):
        tags = []
        print('getTags: ', self._data[0])
        while len(self._data) > 0 and int(self._data[0]) == startByte:
            end_index = 14
            resp = self._data[0:end_index]
            self._data = self._data[end_index + 1:]
            print(self._data)
            print(':'.join('{:02x}'.format(t,2) for t in resp))

            location = resp[1]
            epc = resp[2:]
            tags.append((location, epc))

        return tags

    def processCheckout(self):
        return self.getTags(0x11, 0xa0)






