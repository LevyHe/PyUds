'''
Created on 24 mar 2015

@author: mathias.bergvall
'''
import ctypes

import pyps


SILABS_WRITE_LATCH = 0x00222094
SILABS_GET_PART_NUMBER = 0x00222080


class ConradRelay(pyps.base.Base):

    def __init__(self, port, relay_no=0):
        from . import winioctl
        self.dctl = winioctl.DeviceIoControl(r'\\.\%s' % port)
        self.mask = 1 << int(relay_no)

    def setonoff(self, on):
        if on:
            self._do_write_latch(self.mask, 0x0)
        else:
            self._do_write_latch(self.mask, self.mask)

    def get_part_num(self):
        result = ctypes.c_byte(0)
        with self.dctl:
            status, _ = self.dctl.ioctl(SILABS_GET_PART_NUMBER,
                                        None, 0,
                                        ctypes.pointer(result), ctypes.sizeof(result))
            if not status:
                raise Exception('IOCTL returned failure. GetLastError(): %d' % ctypes.windll.kernel32.GetLastError())
        return result.value

    def _do_write_latch(self, mask, value):
        with self.dctl:
            CommandArray = ctypes.c_byte * 2
            command = CommandArray(mask, value)
            status, _ = self.dctl.ioctl(SILABS_WRITE_LATCH,
                                        ctypes.pointer(command), ctypes.sizeof(CommandArray),
                                        None, 0)
            if not status:
                raise Exception('IOCTL returned failure. GetLastError(): %d' % ctypes.windll.kernel32.GetLastError())
