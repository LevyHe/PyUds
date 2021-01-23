'''
Created on 15 jul 2013

@author: Simon Tegelid
'''

import serial

import pyps


class PPS11815(pyps.base.Base):
    '''
    API for PPS-11815 and equivalents.
    '''
    def __init__(self, port, baud=9600, **kwargs):
        self.ser = serial.Serial(port, baud, timeout=1, xonxoff=True)

    def __del__(self):
        if self.ser.isOpen():
            self.ser.close()

    def setv(self, volts):
        volts = min(99.9, volts)
        self.tx("VOLT%03d" % int(volts * 10))

    def seti(self, amps):
        amps = min(9.99, amps)
        self.tx("CURR%03d" % int(amps * 100))

    def setonoff(self, on):
        self.setv(12 if on else 0)
        # self.tx("SOUT%d"%(1 if on else 0))

    def tx(self, command):
        command += '\r'
        self.ser.write(command)
        return self.rx()

    def rx(self, rspfmt=None):
        rxdata = ""
        while True:
            rx = self.ser.readline().strip()
            if rx == "OK":
                break
            rxdata += rx
        return rxdata

if __name__ == '__main__':
    p = PPS11815('COM13')
    p.setonoff(0)
    p.setv(13)
    p.setv(12)
    p.setonoff(1)
