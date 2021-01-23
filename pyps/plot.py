'''
Created on 15 jul 2013

@author: Simon Tegelid
'''

import pyps
import matplotlib.pyplot as plt


class Plot(pyps.base.PyPsBase):

    def __init__(self, sampletime=1 / 100.):
        self.plt = plt
        self.sampletime = sampletime
        self.volts = []
        self.currenttime = 0.

    def now(self):
        return self.currenttime

    def setv(self, volts):
        self.volts.append(volts)
        self.noop()

    def noop(self):
        self.currenttime += self.sampletime

    def plot(self):
        self.plt.plot(self.volts)
        self.plt.show()

if __name__ == '__main__':
    pass
