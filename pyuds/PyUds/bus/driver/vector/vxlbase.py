# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 10:51:35 2019

@author: levy.he
"""

import ctypes
from . import vxlapy

def stringify(cobj, indent=2):
    s = "%s\n" % type(cobj)
    if issubclass(type(cobj), ctypes.Union):
        cobj = getattr(cobj, cobj._fields_[0][0])
    if issubclass(type(cobj), ctypes.Structure):
        for field in cobj._fields_:
            s += "%s%s=%s\n" % (indent * ' ', field[0], stringify(getattr(cobj, field[0]), indent + 2))
        return s
    try:
        return bytearray(cobj[:])
    except TypeError:
        return "%d (0x%x)" % (cobj, cobj)


def debugwrap(func):
    def caller(*args, **kwargs):
        if hasattr(args[0], 'debug') and args[0].debug:
            print(args[0].__class__.__name__, repr(func), repr(args), repr(kwargs))
        return func(*args, **kwargs)
    return caller

class VxlBaseException(Exception):
    pass


class VxlBaseEvent(object):

    def __str__(self):
        return stringify(getattr(self.event.tagData, self.tagDataAttr))


class VxlBase(object):

    def __init__(self, debug=False, debugapi=False):
        self.api = vxlapy.vxlapy(trace=debugapi)
        # self._app_name = None
        self.debug = debug
        self.initAccess = False
        self.portIsOpen = False
        self.portHandle = vxlapy.XLportHandle(vxlapy.XL_INVALID_PORTHANDLE)
        self.accessMask = vxlapy.XLaccess(0)
        self.permissionMask = vxlapy.XLaccess(0)

        self.api.xlOpenDriver()

    @debugwrap
    def __del__(self):
        self.api.xlCloseDriver()

    @debugwrap
    def getchannelIdx(self, channel=0, app_name=None, busType=vxlapy.XL_INTERFACE_VERSION):
        if app_name is not None:
            hw_type = ctypes.c_uint(0)
            hw_index = ctypes.c_uint(0)
            hw_channel = ctypes.c_uint(0)
            self.api.xlGetApplConfig(
                self._app_name, channel, hw_type, hw_index, hw_channel,busType)
            channelIdx = self.api.xlGetChannelIndex(hw_type.value, hw_index.value,
                                                       hw_channel.value)
            if self.debug:
                print('Channel %d idex %d found'%(channel,channelIdx))
            if channelIdx < 0:
                raise VxlBaseException("No HW port available")
        else:
            channelIdx = channel
        return channelIdx

    @debugwrap
    def getChannelMask(self, busType, channelIdx=1, xlInterfaceVersion=vxlapy.XL_INTERFACE_VERSION):
        driverConfig = vxlapy.XLdriverConfig()
        self.api.xlGetDriverConfig(ctypes.byref(driverConfig))
        for i in range(driverConfig.channelCount):
            if self.debug:
                print("Channel %d cap 0x%x ifver %d" % (i, driverConfig.channel[i].channelBusCapabilities, driverConfig.channel[i].interfaceVersion))
            if (driverConfig.channel[i].channelBusCapabilities & busType and  # eg. XL_BUS_COMPATIBLE_*
                    driverConfig.channel[i].interfaceVersion >= xlInterfaceVersion):  # eg. XL_INTERFACE_VERSION*
                
                if self.accessMask.value == 0 and channelIdx == i:
                    if self.debug:
                        print("Using %s, (sn=%06d, mask=0x%04x)" % (stringify(driverConfig.channel[i].name), driverConfig.channel[i].serialNumber,
                                                                    driverConfig.channel[i].channelMask))
                    self.accessMask.value |= driverConfig.channel[i].channelMask
                    return True
                #channelIdx -= 1
        return False

    @debugwrap
    def openPort(self, busType, userName='vxlapy', accessMask=None, permissionMask=None, rxQueueSize=32768, xlInterfaceVersion=vxlapy.XL_INTERFACE_VERSION_V4):
        if accessMask is not None:
            self.accessMask.value = accessMask
        if permissionMask is not None:
            self.permissionMask.value = permissionMask
        if permissionMask is None and self.accessMask.value != 0:
            self.permissionMask.value = self.accessMask.value
            self.api.xlOpenPort(ctypes.byref(self.portHandle), userName, self.accessMask.value, ctypes.byref(self.permissionMask), rxQueueSize, xlInterfaceVersion, busType)
            self.portIsOpen = True

            self.initAccess = self.permissionMask.value == self.accessMask.value and self.accessMask.value != 0
        else:
            raise VxlBaseException("No HW port available")

    @debugwrap
    def activateChannel(self, bustype):
        return self.api.xlActivateChannel(self.portHandle, self.accessMask, bustype, 0)

    @debugwrap
    def deactivateChannel(self):
        return self.api.xlDeactivateChannel(self.portHandle, self.accessMask)

    @debugwrap
    def flush_rx_buffer(self):
        self.api.xlFlushReceiveQueue(self.portHandle)

    @debugwrap
    def flush_tx_buffer(self):
        self.api.xlCanFlushTransmitQueue(self.portHandle, self.accessMask)

    @debugwrap
    def closePort(self):
        if self.portIsOpen:
            self.api.xlDeactivateChannel(self.portHandle, self.accessMask)
            self.api.xlClosePort(self.portHandle)
            self.api.xlCloseDriver()
            self.portIsOpen = False

    @debugwrap
    def receive(self):
        raise NotImplemented


if __name__ == "__main__":
    b = VxlBase()
