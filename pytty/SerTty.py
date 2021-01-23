#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 10:21:44 2020

@author: levy.he
@file  : SerTty.py
"""
import serial
import io
import codecs
from serial.tools.miniterm import Console



class SerTty(object):

    def __init__(self, port, baudrate=9600, timeout=0.5, **kwargs):
        
        self.ser = serial.Serial(
            port=port, baudrate=baudrate, timeout=timeout, **kwargs)
        
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        self._tx_encoder = codecs.getincrementalencoder('UTF-8')('replace')
        self._rx_decoder = codecs.getincrementaldecoder('UTF-8')('replace')

    def open(self):
        self.ser.open()

    def read(self, size=1):
        return self.ser.read(size)

    def readline(self,size=1):
        return self.sio.readline(size)

    def WriteCmd(self, cmd):
        try:
            cmd += '\n'
            text = self._tx_encoder.encode(cmd)
            for i in text:
                self.ser.write(i)
                ec = self.ser.read(1)
                if ec != i:
                    break
        except serial.SerialException as e:
            print('serial error:', e)

    def WaitEcho(self):
        cmds = ''
        while True:
            data = self.ser.read(self.ser.in_waiting or 1)
            if data:
                data = self._rx_decoder.decode(data)
                cmds += data
                if cmds == '\r\n# ':
                    return
                


    def flush(self):
        self.ser.flush()

    def readbytes(self):
        return self.ser.in_waiting

    def close(self):
        self.ser.close()

if __name__ == '__main__':
    pass
