'''
Created on 24 mar 2015

@author: simon.tegelid
'''
import struct
from collections import namedtuple

import serial
from serial.tools.list_ports import comports

import pyps


Object = namedtuple('Object', ['object', 'access', 'datatype', 'datalength'])

Objects = {'device_type': Object(0, 'ro', '16s', 16),
           'device_serial_no': Object(1, 'ro', '16s', 16),
           'nominal_voltage': Object(2, 'ro', 'f', 4),
           'nominal_current': Object(3, 'ro', 'f', 4),
           'nominal_power': Object(4, 'ro', 'f', 4),
           'device_article_no': Object(6, 'ro', '16s', 16),
           'manufacturer': Object(8, 'ro', '16s', 16),
           'software_version': Object(9, 'ro', '16s', 16),
           'device_class': Object(19, 'ro', 'h', 2),
           'ovp_threshold': Object(38, 'rw', 'h', 2),
           'ocp_threshold': Object(39, 'rw', 'h', 2),
           'set_value_u': Object(50, 'rw', 'h', 2),
           'set_value_i': Object(51, 'rw', 'h', 2),
           'power_supply_control': Object(54, 'rw', 'bb', 2),
           'status_actual_values': Object(71, 'ro', 'bbhh', 6),
           'status_momentary_set_values': Object(72, 'ro', 'bbhh', 6)}


class PS2000B(pyps.base.Base):

    @staticmethod
    def _auto_detect_port():
        for port, name, hid in comports():
            if "PS 2000 B series" in name:
                return port
        raise Exception("Error: Could not locate the power supply com port." +
                        " Is the power supply connected?" +
                        " Have you installed the correct drivers?")

    def __init__(self, port=None, baud=115200, **kwargs):
        self.ser = None

        if port is None:
            port = self._auto_detect_port()

        self.ser = serial.Serial(port, baud, timeout=1, xonxoff=True,
                                 parity=serial.PARITY_ODD)
        self.unom = self.get_unom()
        self.inom = self.get_inom()
        self.set_remote_mode(True)

    def __del__(self):
        if self.ser is not None and self.ser.isOpen():
            self.ser.close()

    def _checksum(self, data):
        return struct.pack('>H', sum(data))

    def tx(self, obj, *data):
        dn = 0  # Hardocoded device node 0
        tx = True
        data_length = len(data) - 1
        direction = 1 if tx else 0
        cast_type = 1 if tx else 0

        # transmission_type = 0  # Reserved
        # transmission_type = 2  # Answer to data
        if obj.access == 'ro':
            transmission_type = 1  # Query data
        elif obj.access == 'rw':
            transmission_type = 3  # Send data
        else:
            raise Exception("Unknown object access %s", obj.access)

        sd = 0
        sd |= (data_length & 0xf)
        sd |= (direction & 0x1) << 4
        sd |= (cast_type & 0x1) << 5
        sd |= (transmission_type & 0x3) << 6

        if len(data) > 0:
            data = struct.pack('>' + obj.datatype, *data)
        data = bytearray([sd, dn, obj.object]) + bytearray(data)
        data += self._checksum(data)

        self.ser.write(data)
        return self.rx(obj)

    def rx(self, obj):
        r = bytearray()
        r += self.ser.read(3)
        sd, dn, object = r
        sd = sd
        sd = r[0]
        data_length = sd & 0xf
        direction = (sd >> 4) & 0x01
        cast_type = (sd >> 5) & 0x01
        transmission_type = (sd >> 6) & 0x03

        r += self.ser.read(data_length + 1)
        r += self.ser.read(2)  # csum

        rx_data = r[3:-2]
        rx_csum = r[-2:]
        calc_csum = self._checksum(r[0:-2])

        if rx_csum != calc_csum:
            raise Exception("Invalid checksum (rx=%s, calc=%s)",
                            rx_csum, calc_csum)

        if object == 0xff and ord(rx_data) != 0:
            raise Exception("Received error %d", ord(rx_data))

        response = None
        if object == obj.object:
            response = struct.unpack('>' + obj.datatype, rx_data)

        return response

    def get_inom(self):
        return self.tx(Objects['nominal_current'])[0]

    def get_unom(self):
        return self.tx(Objects['nominal_voltage'])[0]

    def set_remote_mode(self, on=True):
        return self.tx(Objects['power_supply_control'],
                       0x10, (0x10 if on else 0x00))

    def setv(self, volts):
        return self.tx(Objects['set_value_u'], int((volts * 0x6400) / self.unom + 0.5))

    def seti(self, amps):
        return self.tx(Objects['set_value_i'], int((amps * 0x6400) / self.inom + 0.5))

    def getv(self):
        rx = self.tx(Objects['status_actual_values'])
        volts = (self.unom * rx[2]) / 0x6400
        return volts

    def getcurrenti(self):
        rx = self.tx(Objects['status_actual_values'])
        amps = (self.inom * rx[3]) / 0x6400
        return amps

    def setonoff(self, on):
        return self.tx(Objects['power_supply_control'],
                       0x01, (0x01 if on else 0x00))

    def getonoff(self):
        rx = self.tx(Objects['status_actual_values'])
        return bool(rx[1] & 0x01)

if __name__ == "__main__":
    # import time
    ps = PS2000B("COM10")
    ps.set_remote_mode(1)
    # time.sleep(0.1)
    # ps.setv(5)
    # ps.seti(0.2)
    # ps.setonoff(True)
    # time.sleep(3)
    print(ps.get_unom())
    print(ps.getv())
    print(ps.getcurrenti())
    # ps.setonoff(False)
    ps.set_remote_mode(0)
