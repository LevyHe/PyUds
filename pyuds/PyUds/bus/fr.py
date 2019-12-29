# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 17:34:30 2019

@author: levy.he
"""
import importlib

class FrFrame(object):

    def __getattr__(self, key):
        return self._dict[key]

    def __setattr__(self, key, value):
        super(FrFrame, self).__setattr__(key, value)

    __slots__ = (
        "timestamp",
        "slot_id",
        "base_cycle",
        "repetition_cycle",
        "single_shot",
        "channel",
        "channel_mask",
        "pay_load_length",
        "data",
        "flags",
        "cycle",
        "direction",
        "_dict"                     # see __getattr__
    )

    def __init__(self, timestamp=0.0, slot_id=0, base_cycle=0, direction='Tx',cycle=None,
                 repetition_cycle=1, single_shot=True, channel=0,channel_mask=1,
                 pay_load_length=None, data=None,flags=None):
        self._dict = {}
        self.timestamp = timestamp
        self.slot_id = slot_id
        self.single_shot = single_shot
        self.direction = direction
        self.cycle = cycle
        self.base_cycle = base_cycle
        self.repetition_cycle = repetition_cycle
        self.channel = channel
        self.channel_mask = channel_mask
        self.flags = flags
        if data is None:
            self.data = bytearray()
        elif isinstance(data, bytearray):
            self.data = data
        else:
            try:
                self.data = bytearray(data)
            except TypeError:
                err = "Couldn't create message from {} ({})".format(
                    data, type(data))
                raise TypeError(err)
        if pay_load_length is None:
            self.pay_load_length = int(len(self.data) / 2) + len(self.data) % 2
        else:
            self.pay_load_length = pay_load_length

    def __str__(self):
        field_strings = ["Timestamp: {0:>10.4f}".format(self.timestamp)]
        if self.channel is not None:
            try:
                field_strings.append("Channel: {}".format(self.channel))
            except UnicodeEncodeError:
                pass
        field_strings.append('SlotID:{0:3d}  Cycle: {1}'.format(self.slot_id, self.cycle))
        flag_str = '%04X'%(self.flags) if self.flags is not None else None
        field_strings.append('Flags: {}'.format(flag_str))
        field_strings.append("DLC: {0:3d}".format(self.pay_load_length*2))
        data_strings = ""
        if self.data is not None:
            data_strings = ' '.join(['%02X' % (x) for x in self.data])

        field_strings.append(data_strings)

        return "  ".join(field_strings).strip()

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        args = ["timestamp={}".format(self.timestamp),
                "Slots={:#s}".format(str((self.slot_id,self.base_cycle,self.repetition_cycle)))]
        if self.channel is not None:
            args.append("channel={!r}".format(self.channel))

        data = ["{:#02x}".format(byte) for byte in self.data]
        args += ["PayLoadLength={}".format(self.pay_load_length),
                 "data=[{}]".format(", ".join(data))]

        return "FrFrame.Message({})".format(", ".join(args))

    def __format__(self, format_spec):
        if not format_spec:
            return self.__str__()
        else:
            raise ValueError("non empty format_specs are not supported")

    def __bytes__(self):
        return bytes(self.data)

    def upatebitsvalue(self, value, start_bit, bit_len, byteorder):
        '''
        byteorder in ('big', 'little')
        '''
        mask = 2 ** bit_len - 1
        if byteorder == 'big':
            s_bytes, s_bit = divmod(bit_len - 1, 8)
            sbytes2, sbit2 = divmod(start_bit, 8)
            start_bit = (len(self.data)-1-s_bytes-sbytes2)*8 + sbit2 - s_bit

        l_value = int.from_bytes(self.data, byteorder)
        l_value &= ~(mask << start_bit)
        l_value |= value << start_bit
        self.data = (l_value).to_bytes(8, byteorder)

    def getbitsvaule(self, start_bit, bit_len, byteorder):
        '''
        byteorder in ('big', 'little')
        '''
        mask = 2 ** bit_len - 1
        if byteorder == 'big':
            s_bytes, s_bit = divmod(bit_len - 1, 8)
            sbytes2, sbit2 = divmod(start_bit, 8)
            start_bit = (len(self.data)-1-s_bytes-sbytes2)*8 + sbit2 - s_bit
        l_value = int.from_bytes(self.data, byteorder)
        return (l_value >> start_bit) & mask

    def update_from_msg(self, msg):
        self.timestamp = msg.timestamp
        self.slot_id = msg.slot_id
        self.base_cycle = msg.base_cycle
        self.direction = msg.direction
        self.cycle = msg.cycle
        self.channel = msg.channel
        self.repetition_cycle = msg.repetition_cycle
        self.data = msg.data
        self.single_shot = msg.single_shot
        self.channel_mask = msg.channel_mask
        self.pay_load_length = msg.pay_load_length
        self.flags = msg.flags
        self._dict = msg._dict


class FrBus(object):
    @staticmethod
    def __new__(cls, *args, bus_driver='vector', **kwargs):

        try:
            from . import driver
            bus_module = importlib.import_module(
                "."+bus_driver, package=driver.__package__)
            cls = getattr(bus_module, 'FrBus')
        except Exception as e:
            raise ImportError(
                "Cannot import driver module '{}': {}".format(bus_driver, e)
            )
        return cls(*args, **kwargs)

