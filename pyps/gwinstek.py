'''
Created on 16 jun 2014

@author: Anders Gertz
'''

import serial
import time
import pyps


class PSP2010(pyps.base.Base):
    '''
    API for PSP-2010 and equivalents.
    '''
    def __init__(self, port, baud=2400):
        self.sleeptime = 0.5
        self.ser = None
        self.ser = serial.Serial(port, baud, timeout=1, xonxoff=False)
        self.lastsent = time.clock() - self.sleeptime

    def __del__(self):
        if self.ser is not None and self.ser.isOpen():
            self.ser.close()

    def setv(self, volts):
        volts = max(0.0, min(19.9, volts))
        self.tx("SV %05.2f" % volts)

    def seti(self, amps):
        amps = max(0.0, min(9.99, amps))
        self.tx("SI %.2f" % amps)

    def setonoff(self, on):
        self.tx("KOE" if on else "KOD")

    def tx(self, command):
        s = self.lastsent + self.sleeptime - time.clock()
        if s > 0:
            time.sleep(s)
        self.ser.write(command + '\r')
        self.lastsent = time.clock()

if __name__ == '__main__':
    p = PSP2010('COM1')
    p.setonoff(False)
    p.setv(13)
    p.setv(12)
    p.setonoff(True)
