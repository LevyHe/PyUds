# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 22:14:16 2019

@author: levy.he
"""
import re
import time
from . import FrFrame


class FrSendOnce(FrFrame):

    def __init__(self, bus, **config):
        config['single_shot'] = True
        super(FrSendOnce, self).__init__(**config)
        self._bus = bus

    def __call__(self):
        self._bus.SendOnce(self)


class FrReadOnce(FrFrame):
    
    def __init__(self, bus, timeout=2.0, **config):
        super(FrReadOnce, self).__init__(**config)
        self._bus = bus
        self.timeout = timeout

    def __call__(self, timeout=None):
        msg = self._bus.ReadOnce(self.slot_id, timeout)
        if msg is not None:
            self.update_from_msg(msg)
            return self
        else:
            return None


class FrReader(FrFrame):

    def __init__(self, bus, **config):
        super(FrReader, self).__init__(**config)
        self._bus = bus

    def start(self):
        self._bus.add_reader(self)

    def stop(self):
        self._bus.remove_reader(self)

    def _reader(self, msg):
        self.update_from_msg(msg)

    def __call__(self, msg):
        if msg.slot_id == self.slot_id:
            self._reader(msg)


class FrSender(FrFrame):
    def __init__(self, bus, **config):
        config['single_shot'] = False
        super(FrSender, self).__init__(**config)
        self._bus = bus

    def start(self):
        self.single_shot = False
        self._bus.SendOnce(self)

    def stop(self):
        self.single_shot = True
        self._bus.SendOnce(self)

    def __call__(self):
        self._bus.SendOnce(self)


class FrTimeSender(FrFrame):
   
    def __init__(self, bus, period, **config):
        super(FrTimeSender, self).__init__(**config)
        self._bus = bus
        self.__period = period
        self.__start_time = time.time()
    def start(self):
        self._bus.add_sender(self)

    def stop(self):
        self._bus.remove_sender(self)

    def __call__(self):
        wait_time = time.time() - self.__start_time
        if self.__period is not None and wait_time > self.__period:
            self.__start_time = time.time()
            return self
        else:
            return None

