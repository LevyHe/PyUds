# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 19:38:46 2019

@author: levy.he
"""
import time
import threading
from win32process import SetThreadPriority, THREAD_PRIORITY_TIME_CRITICAL
from win32api import GetCurrentThread
from win32event import CreateEvent, WaitForSingleObject, ResetEvent
from . import wres
from .log import MessageLog

class Sender(object):
    def __init__(self, period, msg):
        self.__period = period
        self.__msg = msg
        self.__start_time = time.time()

    def update_period(self, period):
        self.__period = period
        
    def sender(self):
        return self.__msg

    def __call__(self):
        wait_time = time.time() - self.__start_time
        if wait_time > self.__period:
            self.__start_time = time.time()
            return self.sender()
        else:
            return None
        
class Receiver(object):

    def reader(self, msg):
        pass
    def __call__(self, msg):
        self.reader(msg)

class TpBase(object):
    PDU_TYPE_SF = 0
    PDU_TYPE_MF = 1
    PDU_TYPE_CF = 2
    PDU_TYPE_FC = 3
    PDU_TYPE_LF = 4
    TIME_OUT_ERROR = -2
    PDU_TYPE_NONE = -1

    def GetTpName(self):
        return self.__class__.__name__

    def SendFuncReq(self,data):
        pass
    def SendPhyReq(self, data):
        pass
    def WaitResponse(self, timeout):
        pass
    def WaitReserverMsg(self):
        pass
    def sender(self):
        pass
    def reader(self):
        pass
class BusBase(object):
   
    def send(self):
        pass
    def recv(self):
        pass
    def send_periodic(self):
        pass

    def flush_tx_buffer(self):
        pass

    def shutdown(self):
        pass

class ComBase(object):
    '''object'''

    def __init__(self, bus, rx_poll_interval=0.01, tx_poll_interval=0.005, filters=None):
        self.rx_poll_interval = rx_poll_interval
        self.tx_poll_interval = tx_poll_interval
        self._start_time = 0.0
        self.bus = bus
        self.set_filters(filters)
        self._runing = False
        self._rx_once = False
        self._read_msg = None
        self._read_cond = None
        self._senders = []
        self._readers = []
        self._rx_lock = threading.Lock()
        self._tx_lock = threading.Lock()
        self._tx_event = threading.Event()
        self._tx_event = CreateEvent(None, False, False, 'MsgTxEvent')
        self._rx_event = threading.Event()
        self._wait_event = threading.Event()
        self._rx_thread = None
        self._tx_thread = None
    
    def start(self):
        if self._runing is not True:
            if hasattr(self.bus, "start"):
                self.bus.start()
            self._start_time = time.time()
            self._runing = True
            self._rx_thread = threading.Thread(target=self._rx_task)
            self._rx_thread.start()
            self._tx_thread = threading.Thread(target=self._tx_task)
            self._tx_thread.start()

    def stop(self):
        if self._runing is True:
            self._runing = False
            self._rx_thread.join()
            self._tx_thread.join()
            self.bus.shutdown()

    def add_sender(self, sender):
        ''' please add Sender class object'''
        with self._tx_lock:
            if isinstance(sender, list):
                for s in sender:
                    if s not in self._senders:
                        self._senders.append(s)
            elif callable(sender):
                if sender not in self._senders:
                    self._senders.append(sender)

    def add_reader(self, reader):
        if isinstance(reader, list):
            for r in reader:
                if r not in self._readers:
                    self._readers.append(r)
        elif callable(reader):
            if reader not in self._readers:
                self._readers.append(reader)
    
    def remove_sender(self, sender):
        with self._tx_lock:
            if sender in self._senders:
                self._senders.remove(sender)

    def remove_reader(self, reader):
        if reader in self._readers:
            self._readers.remove(reader)

    def wait(self, timeout):
        self._wait_event.wait(timeout)

    def set_filters(self, filters=None):
        self.filters = filters

    def log_filters(self, msg):
        if self.filters is None:
            return True
        return False

    def SendOnce(self, msg):
        with self._tx_lock:
            self._msg_send(msg)

    def ReadOnce(self, cond, timeout=None):
        self._read_cond = cond
        self._read_msg = None
        self._rx_once = True
        self._rx_event.wait(timeout)
        self._rx_event.clear()
        return self._read_msg

    def MsgCompare(self, msg):
        return False

    def msg_format(self, msg):
        return str(msg)

    #@MessageLog
    def _msg_send(self, msg):
        self.bus.send(msg)

    @MessageLog
    def _msg_read(self, timeout):
        return self.bus.recv(timeout)

    def _rx_task(self):
        SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL)
        while self._runing:
            msg = self._msg_read(self.rx_poll_interval)
            if msg is not None and msg.direction=='Rx':
                if self._rx_once and self.MsgCompare(msg):
                    self._rx_once = False
                    self._read_msg = msg
                    self._rx_event.set()
                for reader in self._readers:
                    reader(msg)
                        
    def _tx_task(self):
        SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL)
        while self._runing:
            end_time = self.tx_poll_interval + time.time()
            with self._tx_lock:
                for sender in self._senders:
                    msg = sender()
                    if type(msg) is list:
                        for m in msg:
                            self._msg_send(m)
                    elif msg is not None:
                        self._msg_send(msg)
            time_left = end_time - time.time()
            time_left = max(0, int(time_left * 1000))
            WaitForSingleObject(self._tx_event, time_left)
            ResetEvent(self._tx_event)
            #self._tx_event.wait(time_left)

class ComCan(ComBase):
    EXT_ID_MASK = 0x80000000

    def msg_format(self, msg):
        time_stamp = msg.timestamp - MessageLog.log_start_time
        field_strings = ["Time:{0:>10.4f}".format(time_stamp)]
        chanel = self.bus.channel_info
        field_strings.append(chanel)
        if msg.is_extended_id:
            arbitration_id_string = "ID: {0:08X}".format(msg.arbitration_id)
        else:
            arbitration_id_string = "ID: {0:04X}".format(msg.arbitration_id)
        field_strings.append(arbitration_id_string.rjust(10, " "))

        flag_string = ''.join([
            "X" if msg.is_extended_id else "S",
            "E" if msg.is_error_frame else " ",
            "R" if msg.is_remote_frame else " ",
            "F" if msg.is_fd else " ",
            "BS" if msg.bitrate_switch else "  ",
            "EI" if msg.error_state_indicator else "  "
        ])
        field_strings.append(flag_string)
        field_strings.append(msg.direction)
        field_strings.append("DLC:{0:2d}".format(msg.dlc))
        data_strings = []
        if msg.data is not None:
            for index in range(0, min(msg.dlc, len(msg.data))):
                data_strings.append("{0:02X}".format(msg.data[index]))
        if data_strings:  # if not empty
            field_strings.append(" ".join(data_strings).ljust(24, " "))
        else:
            field_strings.append(" " * 24)
        return "  ".join(field_strings).strip()

    def ReadOnce(self, id, timeout=None):
        if id > 0x7FF: id = (id & 0x1FFFFFFF) | self.EXT_ID_MASK
        self._rx_event.clear()
        self._read_cond = id
        self._read_msg = None
        self._rx_once = True
        self._rx_event.wait(timeout)
        self._rx_event.clear()
        return self._read_msg

    def MsgCompare(self, msg):
        if msg.is_extended_id:
            msg_id = self.EXT_ID_MASK | msg.arbitration_id
        else:
            msg_id = msg.arbitration_id
        if msg_id == self._read_cond:
            return True
        return False

    def set_filters(self, filters=None):
        if isinstance(filters,list): 
            self.filters = [x | self.EXT_ID_MASK if x > 0x7FF else x for x in filters]
        else:
            self.filters = None

    def log_filters(self, msg):
        if self.filters is None:
            return True
        if msg.is_extended_id:
            msg_id = self.EXT_ID_MASK | msg.arbitration_id
        else:
            msg_id = msg.arbitration_id
        if msg_id in self.filters:
            return True
        return False
class ComCanFd(ComCan):
    pass

class ComFr(ComBase):
   
    def __init__(self,bus, **config):
        super(ComFr, self).__init__(bus,**config)
        self._fr_cycle_setter=[]

    def start(self):
        if self._runing is not True:
            if hasattr(self.bus, "start"):
                self.bus.start()
            self._start_time = time.time()
            self._runing = True
            self._rx_thread = threading.Thread(target=self._sync_task)
            self._rx_thread.start()

    def stop(self):
        if self._runing is True:
            self._runing = False
            self._rx_thread.join()
            self.bus.shutdown()

    def msg_format(self, msg):
        time_stamp = msg.timestamp - MessageLog.log_start_time
        field_strings = ["Time:{0:>10.4f}".format(time_stamp)]
        chanel = self.bus.channel_info
        field_strings.append(chanel)
        id_str = 'SlotID:%03d  Cycle: %02d' % (msg.slot_id, msg.cycle)
        field_strings.append(id_str)

        flag_string = 'Flags: %04X' % (msg.flags)
        field_strings.append(flag_string)
        field_strings.append(msg.direction)
        field_strings.append("DLC:{0:3d}".format(msg.pay_load_length*2))
        data_strings = ""
        if msg.data is not None:
            data_strings = ' '.join(['%02X'%(x) for x in msg.data])

        field_strings.append(data_strings)
        return "  ".join(field_strings).strip()
    def log_filters(self, msg):
        if self.filters is None:
            return True
        if msg.slot_id in self.filters:
            return True
        return False

    def _msg_send(self, msg, timeout=None):
        self.bus.send(msg, timeout)

    def MsgCompare(self, msg):
        if msg.slot_id in self._read_cond:
            return True
        return False

    def ReadOnce(self, *slot_id, timeout=None):
        self._rx_event.clear()
        self._read_cond = slot_id
        self._read_msg = None
        self._rx_once = True
        self._rx_event.wait(timeout)
        self._rx_event.clear()
        return self._read_msg

    def add_fr_cycle_setter(self, fr_cycle_setter):
        self._fr_cycle_setter.append(fr_cycle_setter)

    def _sync_task(self):
        SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL)
        while self._runing:
            status = self.bus.wait_sync(self.rx_poll_interval)
            fr_cycle = self.bus.get_fr_cycle()
            for setter in self._fr_cycle_setter:
                setter(fr_cycle)
            if status == 0:
                self._tx_task()
            elif status > 0:
                self._rx_task()

    def _rx_task(self):
        msg = self._msg_read(self.rx_poll_interval)
        if msg is not None:
            if self._rx_once and self.MsgCompare(msg):
                self._rx_once = False
                self._read_msg = msg
                self._rx_event.set()
            for reader in self._readers:
                reader(msg)

    def _tx_task(self):
        with self._tx_lock:
            for sender in self._senders:
                msg = sender()
                if type(msg) is list:
                    for m in msg:
                        self._msg_send(m, self.tx_poll_interval)
                elif msg is not None:
                    self._msg_send(msg)


class ThreadSafety(object):

    def __init__(self, *bus, time_slice=10000):
        self._bus = bus
        self.time_slice = time_slice
        self.resolution = wres.set_resolution(self.time_slice)
    
    def __enter__(self):
        self.resolution.__enter__()
        for i in self._bus:
            if hasattr(i, 'start'):
                i.start()

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.resolution.__exit__(exc_type, exc_value, exc_trace)
        for i in self._bus:
            if hasattr(i, 'stop'):
                i.stop()


    
