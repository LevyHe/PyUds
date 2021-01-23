# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 09:10:06 2019

@author: levy.he
"""
import sys
import os
import re
import pickle
from pyuds import PyUds
from pyuds import Scripts
from datetime import datetime
from termcolor import color, cprint
from pprint import pprint
Uds_Req_List = (
    "diagRawRequest",
    "diagFuncRequest",
    "SessionControl",
    "ECUReset",
    "ClearDiagnosticInformation",
    "ReadDtcInformation",
    "ReadDataByIdentifier",
    "ReadMemoryByAddress",
    "SecurityAccess",
    "CommunicationControl",
    "ReadDataByPeriodicIdentifier",
    "DynamicallyDefineDataIdentifier",
    "WriteDataByIdentifier",
    "InputOutputControlByIdentifier",
    "RoutineControl",
    "RequestDownload",
    "RequestUpload",
    "TransferData",
    "RequestTransferExit",
    "WriteMemoryByAddress",
    "TesterPresent",
    "ControlDTCSetting"
)


class UdsResponseError(Exception):
    pass

class CmdUds(PyUds.BaseDiagnostic):
   
    def __getattribute__(self, name):
        attr = super(CmdUds, self).__getattribute__(name)
        if name in Uds_Req_List:
            return __class__.Cmd_Print(self, attr)
        else:
            return attr

    def Cmd_Print(self, func):
        def caller(*args, **kwargs):
            cprint("Request : %s" % (func.__name__))
            if 'IsCheck' in kwargs:
                IsCheck = kwargs['IsCheck']
                del kwargs['IsCheck']
            else:
                IsCheck = False
            resp = func(*args, **kwargs)
            if(func.__name__ == 'diagFuncRequest'):
                req_addr = __class__._get_func_addr_str(self)
            else:
                req_addr = __class__._get_request_addr_str(self)
            resp_addr = __class__._get_response_addr_str(self)
            req_value = super(CmdUds, self).__str__()
            resp_value = str(resp)
            cprint("%s:%s" % (req_addr, req_value))
            if resp is None:
                color = 'red'
            elif resp.IsPositiveResponse:
                color = 'green'
            else:
                color = 'red'
            cprint("%s:%s" % (resp_addr, resp_value), fg=color, attrs='bold')
            if IsCheck:
                __class__._resp_process(self, resp)
            return resp
        return caller

    def _get_request_addr_str(self):
        name = super(CmdUds, self).getTpName()
        addr = super(CmdUds, self).getTpAddrInfo()[0]
        if name in ['CanTp', 'CanFdTp']:
            ext = ''
            if addr > 0x7FF:
                ext = 'x'
            return '%03X' % (addr&0x1FFFFFFF) + ext
        elif name == 'FrTp':
            return '%04X' % (addr)
        else:
            return str(addr)

    def _get_func_addr_str(self):
        name = super(CmdUds, self).getTpName()
        addr = super(CmdUds, self).getTpAddrInfo()[1]
        if name in ['CanTp', 'CanFdTp']:
            ext = ''
            if addr > 0x7FF:
                ext = 'x'
            return '%03X' % (addr&0x1FFFFFFF) + ext
        elif name == 'FrTp':
            return '%04X' % (addr)
        else:
            return str(addr)

    def _get_response_addr_str(self):
        name = super(CmdUds, self).getTpName()
        addr = super(CmdUds, self).getTpAddrInfo()[2]
        if name in ['CanTp', 'CanFdTp']:
            ext = ''
            if addr > 0x7FF:
                ext = 'x'
            return '%03X' % (addr&0x1FFFFFFF) + ext
        elif name == 'FrTp':
            return '%04X' % (addr)
        else:
            return str(addr)

    def _resp_process(self, diag_resp):
        if diag_resp is None:
            raise UdsResponseError(color.format(
                'Diag Request not response', fg='red', attrs='bold'))
        elif not diag_resp.IsPositiveResponse:
            raise UdsResponseError(color.format(
                'Diag Request negative response[%02X]' % (diag_resp.NRC), fg='red', attrs='bold'))
class GacUdsCom(object):
   
    def __init__(self,diag,diag_internal, keygen=None):
        self.diag_internal = diag_internal
        self.diag = diag
        #self.diag_internal = PyUds.BaseDiagnostic(None,None)
        self.keygen = keygen

    def GetSecurityKey(self, seed_level, seed):
        if self.keygen is not None:
            return self.keygen(seed_level, seed)[:len(seed)]
        else:
            return seed

    def CRC32(self, data_array):
        crc32 = 0xffffffff
        for data in data_array:
            crc32 ^= data & 0x000000ff
            for i in range(8):
                if crc32 & 1 != 0:
                    crc32 = (crc32 >> 1) ^ 0xedb88320
                else:
                    crc32 = crc32 >> 1
        crc32 ^= 0xffffffff
        return crc32.to_bytes(4, byteorder='big')

    def UdsUnlock(self, level, diag=None):
        if diag is None:
            diag = self.diag
        resp = diag.SecurityAccess(level, IsCheck=True)
        if resp.DataRecord != [0x00]*(len(resp.DataRecord)):
            key = self.GetSecurityKey(level, resp.DataRecord)
            resp = diag.SecurityAccess(level + 1, *key, IsCheck=True)
        return resp

    def EnterBoot(self):
        self.diag.SessionControl(0x03)
        self.diag.SessionControl(0x02)
        self.diag.diagDelay(1)
        self.UdsUnlock(0x61)
        

    def BootUpload(self, addr, length):
        resp = self.diag.RequestUpload(0x00, 0x44, addr, length, IsCheck=True)
        block_size = (resp.DataRecord[1] << 8) + resp.DataRecord[2]
        block_num = length // block_size
        if (length % block_size) != 0:
            block_num += 1
        bin_buf=[]
        for i in range(1, block_num + 1):
            resp = self.diag.TransferData(i,IsCheck=True)
            bin_buf += resp.DataRecord[1:]
        self.diag.RequestTransferExit(IsCheck=True)
        return bin_buf

def write_hex_buf(buf, file_name):
    hex_list = []
    for i in range(0, len(buf), 16):
        s_buf = buf[i:i+16]
        hex_list.append(' '.join(["%02X" % (x) for x in s_buf]))
    with open(file_name, 'w+') as f:
        f.write('\n'.join(hex_list))


def main():
    config = Scripts.UdsConfigParse('UdsConfig.json')
    # dtc_fault_config = DTCFaultConfigLoad(dtc_config_path)
    bus = config.GetBus('CanBus1')
    # diag = CmdUds(uds_client=config.GetUdsClient('CanPhy'))
    # diag_internal = CmdUds(uds_client=config.GetUdsClient('CanInternal'))
    diag = config.GetUdsDiag('CanPhy', diag_cls='CmdUds')
    diag_internal = config.GetUdsDiag('CanInternal', diag_cls='CmdUds')
    key_gen = config.GetKeyGens("GAC_A39")
    uds = GacUdsCom(diag, diag_internal, key_gen)
    with PyUds.ThreadSafety(bus):
        uds.EnterBoot()
#        bin_buf = uds.BootUpload(0xAF000000,0x18000)
#        write_hex_buf(bin_buf, "nvm.hex")
        bin_buf = uds.BootUpload(0x80014000, 0x4000)
        write_hex_buf(bin_buf, "veh.hex")
        bin_buf = uds.BootUpload(0x80010000, 0x4000)
        write_hex_buf(bin_buf, "alog1.hex")
main()




