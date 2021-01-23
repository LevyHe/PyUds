'''
Created on 15 jul 2013

@author: Simon Tegelid
'''

import time
import os
try:
    from configparser import SafeConfigParser as CP
except ImportError:
    from ConfigParser import SafeConfigParser as CP

import pyps


class ConfigParser(CP):
    def __init__(self, configfilename=None):
        CP.__init__(self)

        filename = os.environ.get('PYPS_CONFIG', os.path.join(os.path.expanduser("~"), ".pyps"))

        if configfilename is not None:
            filename = configfilename

        if not os.path.isfile(filename):
            raise Exception("No valid pyps config found ($PYPS_CONFIG: %s, %s: %s, configfilename: %s)" % ('PYPS_CONFIG' in os.environ,
                                                                                                           os.path.join(os.path.expanduser("~"), ".pyps"),
                                                                                                           os.path.isfile(os.path.join(os.path.expanduser("~"), ".pyps")),
                                                                                                           configfilename))
        self.filename = filename
        self.read(filename)

    def getinst(self, obj, classpath):
        ''' Returns an object given a root and a path to the object
        obj: Root package
        classpath: path to class under root
        returns: class
        '''
        def f(obj, attrlist):
            if len(attrlist) > 0:
                attr = attrlist.pop(0)
                return f(getattr(obj, attr), attrlist)
            else:
                return obj
        return f(obj, classpath.split('.'))

    def get_hardware_obj(self):
        return self.getinst(pyps, self.get('hardware', 'path'))


class Base(object):
    @staticmethod
    def open(configfilename=None):
        config = ConfigParser(configfilename)
        hw = config.get_hardware_obj()
        return hw(**dict(config.items('serial')))

    def setv(self, volts):
        raise NotImplementedError

    def now(self):
        return time.clock()

    def rampdeltav(self, from_volts, to_volts, v_per_sec):
        self.rampv(from_volts, to_volts, abs(from_volts - to_volts) / float(v_per_sec))
        self.setv(to_volts)

    def rampv(self, from_volts, to_volts, seconds):
        self.funcv(lambda t: from_volts + t * float(to_volts - from_volts) / seconds, seconds)
        self.setv(to_volts)

    def funcv(self, voltfnc, duration):
        t = 0.
        start = self.now()
        while t < duration:
            v = voltfnc(t)
            self.setv(v)
            t = self.now() - start

if __name__ == "__main__":
    p = pyps.open()
    p.setv(12)    
    p.setonoff(True)
    time.sleep(3)
    p.setonoff(False)
