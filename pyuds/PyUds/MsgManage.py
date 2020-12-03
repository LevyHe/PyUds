# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 22:14:16 2019

@author: levy.he
"""
import re
import time
from . import Message


def try_to_value(s):
    s = s.strip()
    try:
        if s[:2].lower() == '0x':
            return int(s, 16)
        return int(s)
    except:
        try:
            value = float(s)
            return value
        except:
            return None

class DBPaser(object):
   
    def __init__(self, db_path=None):
        if db_path is not None:
            self.db_path = db_path
            self.msg_list = []
            self.ba_param_list=[]
            with open(db_path, 'r') as f:
                self.db_str = f.read()
            self.get_ba_param_list()
            self.msg_list = self.get_db_msgs_all()
    def get_ba_param_list(self):
        for r in self.db_str.splitlines():
            if r[:3] == 'BA_':
                c = r.split(';')[0].split()
                pn = c[1][1:-1]
                if len(c) >=3:
                    if c[2] == 'BO_':
                        self.ba_param_list.append((c[4], pn, c[2], c[3]))
                    elif c[2] == 'SG_':
                        self.ba_param_list.append((c[5], pn, c[2], c[3], c[4]))
                    elif c[2] == 'BU_':
                        self.ba_param_list.append((c[4], pn, c[2], c[3]))
                    elif len(c) == 3:
                        self.ba_param_list.append((c[2], pn, c[0]))
    def get_msg_param(self, msg_id, param_name):
        for s in self.ba_param_list:
            if s[2] == 'BO_' and s[1] == param_name and s[3] == str(msg_id):
                return s[0]
        return '0'
    def get_signal_param(self, msg_id, sig_name, param_name):
        for s in self.ba_param_list:
            if s[2] == 'SG_' and s[1] == param_name and s[3] == str(msg_id) and s[4] == sig_name:
                return s[0]
        return '0'
    def get_db_msg(self, name):
        return self.msg_list[name]

    def get_db_msgs_all(self):
        msg = {}
        msg_list = {}
        for r in self.db_str.splitlines():
            if not bool(msg):
                if r[:4] == 'BO_ ':
                    c = r.split(':')
                    nm = c[0].split() + c[1].split()
                    MsgID = try_to_value(nm[1])
                    dlc= try_to_value(nm[3])
                    cycle = self.get_msg_param(nm[1], 'GenMsgCycleTime')
                    cycle = try_to_value(cycle)
                    MsgName=nm[2]
                    msg = dict(MsgID=int(MsgID), dlc=int(
                        dlc), cycle=int(cycle))
                    sig_list = {}
                    msg_list[MsgName]=msg
            else:
                c = r.strip()
                if r[:1] == ' ' and c[:4] == 'SG_ ':
                    c = c.split(':')
                    nm = c[0].split() + c[1].split()
                    bp = re.split('[|@]+', nm[2])
                    start_bit = try_to_value(bp[0])
                    length = try_to_value(bp[1])
                    _type = try_to_value(bp[2][0])
                    StartValue = self.get_signal_param(msg['MsgID'], nm[1], 'GenSigStartValue')
                    _value = try_to_value(StartValue)
                    sig = dict(start_bit=int(start_bit), length=int(
                        length), type=int(_type), value=int(_value))
                    sig_list[nm[1]] = sig
                else:
                    msg['sig_list'] = sig_list
                    msg = {}
        return msg_list


class DBMessage(Message):
    def __setattr__(self, key, value):
        if key not in self.__dict__['_signal'].keys():
            super(DBMessage, self).__setattr__(key, value)
        else:
            bit_len = self.__dict__['_signal'][key]['length']
            mask = 2 ** bit_len - 1
            value = value & mask
            self.__dict__['_signal'][key]['value'] = value
            self._signal_to_data(self.__dict__['_signal'][key])

    def __getattr__(self, key):
        if key in self.__dict__['_signal'].keys():
            value = self.__dict__['_signal'][key]['value']
            return value
        else:
            return self.__dict__[key]

    def __init__(self, db_obj):
        tx_id = db_obj['MsgID']
        dlc = db_obj['dlc']
        is_fd = True if dlc > 8 else False
        if tx_id > 0X7FF:
            ext_id = True
            msg_id = tx_id & 0x1FFFFFFF
        else:
            ext_id = False
            msg_id = tx_id & 0x7FF
        self.__dict__['_signal'] = db_obj['sig_list'].copy()
        super(DBMessage, self).__init__(arbitration_id=msg_id, is_fd=is_fd,
                                        data=[0x00]*dlc, is_extended_id=ext_id)
        for i in self.__dict__['_signal'].keys():
            self._signal_to_data(self.__dict__['_signal'][i])

    def keys(self):
        return self.__dict__['_signal'].keys()

    def __getitem__(self, key):
        if key not in self.keys():
            raise KeyError('Not supported keys: '+key)
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        if key not in self.keys():
            raise KeyError('Not supported keys: '+key)
        self.__setattr__(key, value)

    def __delitem__(self, key):
        if key not in self.keys():
            raise KeyError('Not supported keys: '+key)
        del self.__dict__['_signal'][key]

    def _signal_to_data(self, sig):
        bit_len = sig['length']
        mask = 2 ** bit_len - 1
        start_bit = sig['start_bit']
        _type = sig['type']
        if _type == 0:
            s_bytes, s_bit = divmod(bit_len - 1, self.dlc)
            sbytes2, sbit2 = divmod(start_bit, self.dlc)
            start_bit = (7-s_bytes-sbytes2)*self.dlc + sbit2 - s_bit
        byteorder = ('big', 'little')[_type]
        l_value = int.from_bytes(self.data, byteorder)
        l_value &= ~(mask << start_bit)
        l_value |= sig['value'] << start_bit
        self.data = (l_value).to_bytes(self.dlc, byteorder)

    def _get_signal_from_data(self, sig):
        bit_len = sig['length']
        mask = 2 ** bit_len - 1
        start_bit = sig['start_bit']
        _type = sig['type']
        if _type == 0:
            s_bytes, s_bit = divmod(bit_len - 1, self.dlc)
            sbytes2, sbit2 = divmod(start_bit, self.dlc)
            start_bit = (7-s_bytes-sbytes2)*self.dlc + sbit2 - s_bit
        byteorder = ('big', 'little')[_type]
        l_value = int.from_bytes(self.data, byteorder)
        return (l_value >> start_bit) & mask

class DBMsgReadOnce(DBMessage):
   
    def __init__(self, bus, db_obj, timeout=None):
        super(DBMsgReadOnce, self).__init__(db_obj)
        self._bus = bus
        if timeout is not None:
            self.timeout = timeout
        elif db_obj['cycle'] != 0:
            self.timeout = db_obj['cycle'] / 500.0
        else:
            self.timeout = 2.0
    
    def __call__(self,timeout=None):
        if self.is_extended_id:
            msg_id = self.arbitration_id | 0x80000000
        else:
            msg_id = self.arbitration_id
        if timeout is None:
            timeout = self.timeout
        msg = self._bus.ReadOnce(msg_id, timeout)
        if msg is not None:
            self.update_from_msg(msg)
            for key in self.keys():
                value = self._get_signal_from_data(self._signal[key])
                self._signal[key]['value'] = value
            return self
        else:
            return None


class DBMsgSendOnce(DBMessage):
   
    def __init__(self, bus, db_obj):
        super(DBMsgSendOnce, self).__init__(db_obj)
        self._bus = bus

    def __call__(self):
        self._bus.SendOnce(self)

class DBMsgReader(DBMessage):
    '''
    create a object that can be cycle update
    this object should be add to bus by add_reader
    '''

    def __init__(self, bus, db_obj):
        super(DBMsgReader, self).__init__(db_obj)
        self._bus = bus

    def start(self):
        self._bus.add_reader(self)

    def stop(self):
        self._bus.remove_reader(self)

    def _reader(self, msg):
        self.update_from_msg(msg)
        for key in self.keys():
            value = self._get_signal_from_data(self._signal[key])
            self._signal[key]['value'] = value

    def __call__(self, msg):
        if msg.is_extended_id == self.is_extended_id and msg.arbitration_id == self.arbitration_id:
            self._reader(msg)


class DBMsgSender(DBMessage):
    '''
    create a object to cycle send the message
    this object should be add to bus by add_sender
    '''

    def __init__(self, bus, db_obj):
        super(DBMsgSender, self).__init__(db_obj)
        self._bus = bus
        if db_obj['cycle'] == 0:
            self.__period = None
        else:
            self.__period = db_obj['cycle'] / 1000.0
            self._tx_count = int(self.__period / self._bus.tx_poll_interval + 0.5)
        self._cycle = 0    
        self.__start_time = time.time()

    def start(self):
        self._bus.add_sender(self)

    def stop(self):
        self._bus.remove_sender(self)

    def __call__(self):
        wait_time = time.time() - self.__start_time
        self._cycle += 1
        if self.__period is not None and (wait_time > self.__period or self._cycle >= self._tx_count):
            self._cycle = 0
            self.__start_time = time.time()
            return self
        else:
            return None



class CanMsgSendOnce(Message):

    def __init__(self, bus, **config):
        super(CanMsgSendOnce, self).__init__(**config)
        self._bus = bus

    def __call__(self):
        self._bus.SendOnce(self)

class CanMsgReadOnce(Message):
    
    def __init__(self, bus, timeout=2.0, **config):
        super(CanMsgReadOnce, self).__init__(**config)
        self._bus = bus
        self.timeout = timeout

    def __call__(self,timeout=None):
        if self.is_extended_id:
            msg_id = self.arbitration_id | 0x80000000
        else:
            msg_id = self.arbitration_id
        if timeout is None:
            timeout = self.timeout
        msg = self._bus.ReadOnce(msg_id, timeout)
        if msg is not None:
            self.update_from_msg(msg)
            return self
        else:
            return None

class CanMsgReader(Message):

    def __init__(self, bus, **config):
        super(CanMsgReader, self).__init__(**config)
        self._bus = bus

    def start(self):
        self._bus.add_reader(self)

    def stop(self):
        self._bus.remove_reader(self)

    def _reader(self, msg):
        self.update_from_msg(msg)

    def __call__(self, msg):
        if msg.arbitration_id == self.arbitration_id and msg.is_extended_id == self.is_extended_id:
            self._reader(msg)


class CanMsgSender(Message):

    def __init__(self, bus, period, **config):
        super(CanMsgSender, self).__init__(**config)
        self._bus = bus
        self.__period = period
        self.__start_time = time.time()
        self._tx_count = int(self.__period / self._bus.tx_poll_interval + 0.5)
        self._cycle = 0    
    def start(self):
        self._bus.add_sender(self)

    def stop(self):
        self._bus.remove_sender(self)

    def __call__(self):
        wait_time = time.time() - self.__start_time
        self._cycle += 1
        if self.__period is not None and (wait_time > self.__period or self._cycle >= self._tx_count):
            self._cycle = 0
            self.__start_time = time.time()
            return self
        else:
            return None
