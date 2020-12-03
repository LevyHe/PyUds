# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 20:52:26 2019

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
from ExcelParse import ExcelToJson as EJ



class UdsResponseError(Exception):
    pass

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

class TestUdsCom(object):

    def __init__(self,diag, wake_msg, keygen=None):
        self.wake_msg = wake_msg
        self.diag = diag
        self.keygen = keygen

    def GetSecurityKey(self, seed_level, seed):
        if self.keygen is not None:
            return self.keygen(seed_level, seed)[:len(seed)]
        else:
            return seed

    def UdsUnlock(self, level, diag=None):
        if diag is None:
            diag = self.diag
        resp = diag.SecurityAccess(level, IsCheck=True)
        if resp.DataRecord != [0x00]*(len(resp.DataRecord)):
            key = self.GetSecurityKey(level, resp.DataRecord)
            resp = diag.SecurityAccess(level + 1, *key, IsCheck=True)
        return resp

    def UdsCmd(self):
        print('Please input request diagnostic cmd or exit:')
        self._uds_cmd_process(self.diag)

    def GacClearDTC(self):
        self.diag.ClearDiagnosticInformation(0xFFFFFF, IsCheck=True)

    
    def _uds_cmd_process(self, diag):
        while 1:
            cmds = input()
            if cmds in ('exit', 'quit'):
                diag.StopTesterPresent()
                return
            elif cmds == 'start':
                diag.StartTesterPresent()
                print('Start Send TesterPresent')
            elif cmds == 'stop':
                diag.StopTesterPresent()
                print('Stop Send TesterPresent')
            elif cmds.startswith('unlock'):
                ls = cmds.split()
                if len(ls) < 2:
                    print('please input the unlock level:')
                else:
                    level = int('0x'+ls[1], 16)
                    self.UdsUnlock(level, diag=diag)
            else:
                for cmd in self._get_cmd_list(cmds):
                    diag.diagRawRequest(*cmd)


    def _get_cmd_list(self, cmd):
        cmd_list = []
        parten = r"[^;0-9A-Fa-f\s]"
        result = re.search(parten, cmd)
        if result is not None:
            print('print unknown cmd or position %d, [%s] is not a hex value'%(result.start(), cmd[result.start()]))
            return []
        l1 = cmd.split(';')
        for l in l1:
            parten = r"[0-9A-Fa-f]{1,2}"
            result = re.findall(parten, l)
            hex_list = [int('0x' + x, 16) for x in result]
            cmd_list.append(hex_list)
        return cmd_list

def main(args):
    global dtc_fault_config
    config = Scripts.UdsConfigParse('UdsConfig.json')
    bus = config.GetBus('CanBus1')
    diag = config.GetUdsDiag('CanUds', diag_cls='CmdUds')
    wake_msg = config.GetMessage('NMWeakUp')
    uds = TestUdsCom(diag, wake_msg, None)
    Cmds = {
        'uds': uds.UdsCmd,
    }
    with PyUds.ThreadSafety(bus):
        try:
            wake_msg.start()
            Cmds[args[0]](*args[1:])
        except UdsResponseError as ex:
            print(ex)
        except KeyError as ex:
            print(ex)
            print('Please input cmd in:', Cmds.keys())
        except TypeError as ex:
            print(ex)
            desc = '~~~~~~~~~~~~~~example~~~~~~~~~~~~~\n'
            desc += '  uds: enter diagnostic mode\n'
            print(desc)
        finally:
            wake_msg.stop()

def argv_process(args):
    cmds = args[:1]
    if args[0] == 'boot':
        for file in args[1:]:
            pfile = os.path.abspath(file)
            cmds.append(pfile)
    else:
        cmds = args[:]
    return cmds


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmds = argv_process(sys.argv[1:])
        wk_path = os.path.join(os.path.dirname(__file__), 'pcan_scripts')
        os.chdir(wk_path)
        main(cmds)
    else:
        desc = 'please used with following args:\n'
        desc += '  uds: enter diagnostic mode\n'
        print(desc)
    pass
