# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 17:34:30 2019

@author: levy.he
"""
import importlib
import os
import sys

class Message(object):

    def __getattr__(self, key):
        return self._dict[key]

    def __setattr__(self, key, value):
        super(Message, self).__setattr__(key, value)

    __slots__ = (
        "timestamp",
        "arbitration_id",
        "is_extended_id",
        "is_remote_frame",
        "is_error_frame",
        "channel",
        "dlc",
        "data",
        'direction',
        "is_fd",
        "bitrate_switch",
        "error_state_indicator",
        "__weakref__",              # support weak references to messages
        "_dict"                     # see __getattr__
    )

    def __init__(self, timestamp=0.0, arbitration_id=0, is_extended_id=False,
                 is_remote_frame=False, is_error_frame=False, channel=None,
                 dlc=None, data=None, direction='Tx',
                 is_fd=False, bitrate_switch=False, error_state_indicator=False):
        self._dict = {}
        self.timestamp = timestamp
        self.arbitration_id = arbitration_id
        if is_extended_id is not None:
            self.is_extended_id = is_extended_id

        self.is_remote_frame = is_remote_frame
        self.is_error_frame = is_error_frame
        self.channel = channel
        self.direction = direction
        self.is_fd = is_fd
        self.bitrate_switch = bitrate_switch
        self.error_state_indicator = error_state_indicator
        if data is None or is_remote_frame:
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
        if dlc is None:
            self.dlc = len(self.data)
        else:
            self.dlc = dlc

    def __str__(self):
        field_strings = ["Time:{0:>10.4f}".format(self.timestamp)]
        if self.channel is not None:
            try:
                field_strings.append("Channel: {}".format(self.channel))
            except UnicodeEncodeError:
                pass
        if self.is_extended_id:
            arbitration_id_string = "ID: {0:08X}".format(self.arbitration_id)
        else:
            arbitration_id_string = "ID: {0:04X}".format(self.arbitration_id)
        field_strings.append(arbitration_id_string.rjust(10, " "))

        flag_string = ''.join([
            "X" if self.is_extended_id else "S",
            "E" if self.is_error_frame else " ",
            "R" if self.is_remote_frame else " ",
            "F" if self.is_fd else " ",
            "BS" if self.bitrate_switch else "  ",
            "EI" if self.error_state_indicator else "  "
        ])
        field_strings.append(flag_string)
        field_strings.append(self.direction)
        field_strings.append("DLC: {0:2d}".format(self.dlc))
        data_strings = []
        if self.data is not None:
            for index in range(0, min(self.dlc, len(self.data))):
                data_strings.append("{0:02X}".format(self.data[index]))
        if data_strings:  # if not empty
            field_strings.append(" ".join(data_strings).ljust(24, " "))
        else:
            field_strings.append(" " * 24)

        if (self.data is not None) and (self.data.isalnum()):
            field_strings.append("'{}'".format(
                self.data.decode('utf-8', 'replace')))

        return "  ".join(field_strings).strip()

    def __len__(self):
        return self.dlc

    def __repr__(self):
        args = ["timestamp={}".format(self.timestamp),
                "arbitration_id={:#x}".format(self.arbitration_id),
                "extended_id={}".format(self.is_extended_id)]

        if self.is_remote_frame:
            args.append("is_remote_frame={}".format(self.is_remote_frame))

        if self.is_error_frame:
            args.append("is_error_frame={}".format(self.is_error_frame))

        if self.channel is not None:
            args.append("channel={!r}".format(self.channel))

        data = ["{:#02x}".format(byte) for byte in self.data]
        args += ["dlc={}".format(self.dlc),
                 "data=[{}]".format(", ".join(data))]

        if self.is_fd:
            args.append("is_fd=True")
            args.append("bitrate_switch={}".format(self.bitrate_switch))
            args.append("error_state_indicator={}".format(
                self.error_state_indicator))

        return "can.Message({})".format(", ".join(args))

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
        self.arbitration_id = msg.arbitration_id
        self.is_extended_id = msg.is_extended_id
        self.is_remote_frame = msg.is_remote_frame
        self.is_error_frame = msg.is_error_frame
        self.channel = msg.channel
        self.dlc = msg.dlc
        self.data = msg.data
        self.direction = msg.direction
        self.is_fd = msg.is_fd
        self.bitrate_switch = msg.bitrate_switch
        self.error_state_indicator = msg.error_state_indicator


class CanBus(object):
    @staticmethod
    def __new__(cls, *args, bus_driver='vector', **kwargs):
        # if 'bus_driver' in kwargs:
        #     bus_driver = kwargs['bus_driver']
        #     del kwargs['bus_driver']
        # else:
        #     bus_driver = 'vector'
        try:
            from . import driver

            # bus_module = getattr(driver, bus_driver)
            # pack_path = os.path.join(os.path.dirname(
            #     __file__), 'driver')
            # sys.meta_path.append(pack_path)
            # print(pack_path)
            # pack_path = '.driver.'+bus_driver
            # bus_module = __import__(pack_path)
            # module_name = bus_driver
            # spec = importlib.util.find_spec('.'+bus_driver)
            # print(spec)
            # spec = importlib.util.spec_from_file_location(
            #     pack_path, '.')
            # bus_module = importlib.util.module_from_spec(spec)
            # spec.loader.exec_module(bus_module)
            # bus_module = getattr(driver, bus_driver)
            
            bus_module = importlib.import_module(
                "."+bus_driver, package=driver.__package__)
            cls = getattr(bus_module, 'CanBus')
        except Exception as e:
            raise ImportError(
                "Cannot import driver module '{}': {}".format(bus_driver, e)
            )
        return cls(*args, **kwargs)


class CanFdBus(object):
    @staticmethod
    def __new__(cls, *args, bus_driver='vector', **kwargs):
        try:
            from . import driver
            bus_module = importlib.import_module(
                "."+bus_driver, package=driver.__package__)
            cls = getattr(bus_module, 'CanFdBus')
        except Exception as e:
            raise ImportError(
                "Cannot import driver module '{}': {}".format(bus_driver, e)
            )
        return cls(*args, **kwargs)
