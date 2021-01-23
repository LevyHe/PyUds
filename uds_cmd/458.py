#!C:\Python\Anaconda3\python.exe
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 20:52:26 2019

@author: levy.he
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import re
import pickle
import time
import threading
from pyuds import PyUds
from pyuds import Scripts
from datetime import datetime
from termcolor import color, cprint
from ExcelParse import ExcelToJson as EJ
from struct import Struct
from CddParse import Cdd
from argparse import ArgumentParser, Namespace, ArgumentError
import traceback
from SGMApi import ProvisionKey


flash_driver = (0x91,0x00,0x80,0xFF,0xD9,0xFF,0x10,0x02,0x54,0xFF,0x16,0x08,0x3B,0x80,0x00,0x00,0x7E,0x03,0x82,0x12,0x00,0x90,0x91,0x00,0xF0,0x2A,0xD9,0x22,0x54,0x55,0xDA,0xFA,0x74,0x2F,0x91,0x30,0x00,0x4F,0x19,0x4F,0x30,0x36,0xB7,0x0F,0x08,0xF0,0x96,0xF1,0x59,0x4F,0x30,0x36,0x0D,0x00,0xC0,0x04,0xB7,0x2F,0x04,0xF0,0x59,0x4F,0x30,0x36,0x0D,0x00,0xC0,0x04,0x91,0x10,0xF0,0x5A,0x59,0x54,0x90,0x9A,0x8F,0xF5,0x0F,0xF1,0x59,0x5F,0x98,0x9A,0xDA,0x80,0x59,0x5F,0xA8,0xAA,0xDA,0x50,0x59,0x5F,0xA8,0xAA,0x0D,0x00,0x80,0x04,0x19,0x4F,0x30,0x36,0xB7,0x0F,0x08,0xF0,0x96,0xF1,0x59,0x4F,0x30,0x36,0x0D,0x00,0xC0,0x04,0xB7,0x3F,0x04,0xF0,0x59,0x4F,0x30,0x36,0x0D,0x00,0xC0,0x04,0x82,0x04,0x02,0x40,0xC5,0xF4,0x10,0x00,0x54,0x41,0xBB,0x00,0x00,0x5B,0x9B,0x15,0xB7,0x50,0x3B,0x00,0x98,0x23,0x9B,0x02,0x60,0x20,0x3C,0x03,0x54,0x40,0xA2,0x10,0x54,0xF3,0x26,0x23,0xF6,0x33,0x3F,0x50,0xFB,0xFF,0x7F,0x50,0x2B,0x80,0x91,0x00,0x80,0x5F,0x39,0x50,0x11,0x02,0x39,0x51,0x11,0x02,0x37,0x01,0xE1,0xF2,0x6F,0x40,0x21,0x80,0xEE,0x1F,0x54,0x41,0x82,0x00,0x3C,0x06,0x54,0xFF,0x2E,0xB2,0x82,0x14,0x54,0x40,0xA2,0x10,0x54,0xFF,0x2E,0x34,0xF6,0x43,0x3F,0x50,0xF8,0xFF,0x91,0x00,0x80,0xFF,0x39,0xFF,0x13,0x02,0x37,0x0F,0x61,0xF1,0x39,0xF1,0x13,0x02,0x37,0x01,0xE1,0x10,0x7F,0x50,0x07,0x80,0xF6,0x46,0xEE,0x02,0x76,0x14,0x82,0x24,0x3C,0x02,0x82,0x14,0x02,0x42,0xDA,0xFA,0x74,0x2F,0x00,0x90,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0x91,0x00,0x80,0xFF,0xD9,0xFF,0x10,0x02,0x82,0x0B,0x20,0x08,0x02,0xB3,0x02,0xB6,0x54,0xF0,0x3B,0x80,0x00,0x10,0x91,0x00,0xF0,0x2A,0xD9,0x22,0x54,0x55,0x8F,0x80,0x00,0xF1,0x7E,0x14,0x82,0x1B,0x1D,0x00,0xDA,0x00,0x3B,0xA0,0x0F,0x10,0x74,0x21,0x3B,0x00,0x28,0x20,0xC5,0xF5,0x10,0x00,0x3B,0x00,0x20,0x73,0x7B,0x00,0xF0,0x8A,0x3B,0x00,0x0A,0x90,0x1D,0x00,0xC8,0x00,0x91,0x30,0x00,0x6F,0xD9,0x66,0x30,0x36,0x54,0x60,0xB7,0x00,0x08,0xF0,0x96,0xF1,0x74,0x6F,0x0D,0x00,0xC0,0x04,0xB7,0x2F,0x04,0x00,0x74,0x60,0x0D,0x00,0xC0,0x04,0xDA,0x50,0x74,0x2F,0x0D,0x00,0x80,0x04,0x54,0x60,0xB7,0x00,0x08,0xF0,0x96,0xF1,0x74,0x6F,0x0D,0x00,0xC0,0x04,0xB7,0x3F,0x04,0xF0,0x74,0x6F,0x0D,0x00,0xC0,0x04,0x54,0x50,0x3C,0x03,0x54,0x56,0xA2,0x06,0x54,0xFF,0x26,0x7F,0xEE,0x03,0x3F,0x26,0xFB,0xFF,0x54,0xFF,0x3B,0x00,0x00,0x02,0x26,0x0F,0x54,0xF0,0x3B,0x00,0x00,0xA1,0x26,0xA0,0x7F,0x26,0x04,0x80,0xEE,0x02,0x76,0x04,0x82,0x1B,0x1D,0x00,0x90,0x00,0x3B,0x00,0x10,0xA0,0x3F,0xA5,0x08,0x80,0x8F,0xF4,0x0F,0xF1,0xEE,0x04,0x3B,0xA0,0x07,0xB0,0x3C,0x05,0x3B,0xA0,0x0A,0xB0,0x3B,0x00,0x02,0xA0,0x54,0x60,0xB7,0x00,0x08,0xF0,0x96,0xF1,0x74,0x6F,0x0D,0x00,0xC0,0x04,0xB7,0x2F,0x04,0x00,0x74,0x60,0x0D,0x00,0xC0,0x04,0x82,0x0C,0x8F,0xEA,0x1F,0x00,0xC2,0xF0,0x60,0x07,0x8F,0x1C,0x00,0xF1,0x8F,0x2F,0x00,0x00,0x1B,0x00,0x5F,0x05,0xA6,0x80,0x60,0x0C,0x44,0x4F,0x74,0xCF,0xC2,0x1C,0xFC,0x75,0x91,0x00,0x80,0x7F,0xD9,0x77,0x11,0x02,0x14,0x7F,0x2E,0x43,0x82,0x1B,0x3C,0x50,0x91,0x10,0xF0,0xCA,0x59,0xC4,0x90,0x9A,0x59,0xC3,0x98,0x9A,0x59,0xC9,0xA8,0xAA,0x59,0xCB,0xA8,0xAA,0x0D,0x00,0x80,0x04,0xDA,0x00,0x74,0xAF,0x54,0x5B,0x3B,0x10,0x38,0xC0,0x06,0x7C,0x3B,0x00,0x98,0xD3,0x9B,0x0D,0x60,0xD0,0x3C,0x03,0x54,0x5F,0xA2,0xBF,0x54,0xF0,0x26,0xD0,0xF6,0x03,0x3F,0xCF,0xFB,0xFF,0x7F,0xCF,0x2A,0x80,0x14,0x70,0x14,0x7F,0x37,0x0F,0xE1,0xF2,0x6F,0x40,0x24,0x80,0xEE,0x22,0x54,0x5B,0x82,0x00,0x3C,0x07,0x54,0xFF,0x2E,0xB3,0xDA,0x01,0x74,0xAF,0x54,0x50,0xA2,0xB0,0x54,0xFF,0x2E,0x35,0x54,0xAF,0xEE,0x03,0x3F,0xC0,0xF6,0xFF,0x91,0x00,0x80,0x7F,0x39,0x7F,0x13,0x02,0x37,0x0F,0x61,0xB1,0x39,0x7F,0x13,0x02,0x37,0x0F,0xE1,0xD0,0x7F,0xC0,0x08,0x80,0x54,0xAF,0xEE,0x07,0xF6,0xB2,0x76,0xD5,0xDA,0x02,0x3C,0x02,0xDA,0x01,0x74,0xAF,0x54,0xAB,0xF6,0xB3,0xA2,0xA5,0x42,0xA4,0x74,0x21,0x54,0x6F,0xB7,0x0F,0x08,0xF0,0x96,0xF1,0x74,0x6F,0x0D,0x00,0xC0,0x04,0xB7,0x3F,0x04,0xF0,0x74,0x6F,0x0D,0x00,0xC0,0x04,0x76,0x53,0xDF,0x0B,0x39,0x7F,0xDA,0xF0,0x74,0x2F,0x02,0xB2,0x00,0x90,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0xAD,0xF0,0x8F,0x00,0x66,0xBF,0x21,0x3E)

can_node_config = (0xFF, 0xFF, 0x1F, 0x00)

car_config = (0xFF, 0x0C, 0x0F, 0x55, 0x03, 0x00, 0x00, 0x00)

dtc_fault_config = None
dtc_fault_pickle_path = 'dtc_fault_config.pick'
cdd_did_print = None
OutputDir = os.getcwd()

class UdsResponseError(Exception):
    pass

ASCII_DID_LIST = (0xD919,0xD92A)

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

DTC_STATUS = {
    0x00: ("Pass",'green', None, 'bold'),
    0x09: ("Failed",'red', None, 'bold'),
    0x08: ("History", 'white', None, None),
}

DNV_FAULT_STATUS = {
    0x00: ("Pass",'green', None, 'bold'),
    0x09: ("Failed",'red', None, 'bold'),
    0x08: ("History", 'cyan', None, 'bold'),
    0x40: ("NotReport", 'white', None, None),
}

DNVCriticalEventConfig={}

UNKNOWN_STATUS = ('Unknown', 'magenta', None, None)

{
    "DTC": ("DTC_Name", "desc")
}
{
    "EventID":("DTC","EVENT_NAME","desc")
}

class UdsArgumentParser(ArgumentParser):
   
    def exit(self, status=0, message=None):
        raise Exception(message)

    def error(self, message):
        cprint(message, fg='green', attrs='bold')
        raise Exception(message)

    def _get_cmd_list(self, cmd):
        cmd_list = []
        parten = r"[^;0-9A-Fa-f\s]"
        result = re.search(parten, cmd)
        if result is not None:
            return []
        l1 = cmd.split(';')
        for l in l1:
            parten = r"[0-9A-Fa-f]{1,2}"
            result = re.findall(parten, l)
            hex_list = [int('0x' + x, 16) for x in result]
            cmd_list.append(hex_list)
        return cmd_list

    def GetSubParser(self):
        self._subparser = self.add_subparsers(title='Supported commands', metavar='')
        return self

    def SubArgObj(self, name, **kwargs):
        return name, kwargs

    def Add_SubArgs(self, sub_cmd, *sub_args, help=None):
        parser_cmd = self._subparser.add_parser(sub_cmd, help=help)
        for arg in sub_args:
            parser_cmd.add_argument(arg[0], **arg[1])
        parser_cmd.set_defaults(cmd=sub_cmd)

    def ParseArgStr(self, arg_str):
        cmds = self._get_cmd_list(arg_str)
        if cmds and arg_str:
            return Namespace(cmd='uds',value=cmds)
        else:
            p = self.parse_args(arg_str.split())
            cmd = getattr(p, 'cmd', None)
            if cmd == 'uds':
                p.value = self._get_cmd_list(' '.join(p.value))
            return p

class CddDidPrint(dict):

    def __init__(self, cdd_path):
        self.Dids={}
        try:
            self.cdd = Cdd(cdd_path)
            self.Dids = self.cdd.Parse_AllDids()
        except:
            cprint('Warning: %s is not a valid cdd file, Cdd Print Function will be disabled'%(cdd_path), fg='yellow', attrs='bold')
        super(CddDidPrint, self).__init__()
        self.update(self.Dids)

    def _did_print(self, did, Data):
        obj = self.get(did, None)
        indent = 4
        if obj:
            cprint("%s"%(obj['DidName']), fg='green', attrs='bold')
            for dt in obj['DataList']:
                if dt['ObjType'] == 'Raw':
                    rv_str, pv_str = self._did_format(dt, Data)
                    print_list = []
                    print_list.append(' ' * indent)
                    print_list.append(color.format(dt['Name'], fg='green', attrs='bold'))
                    print_list.append('-')
                    print_list.append(color.format(rv_str, fg='blue', attrs='bold'))
                    print_list.append('-')
                    print_list.append(color.format(pv_str, fg='yellow', attrs='bold'))
                    print_list.append(' ')
                    print_list.append(color.format(dt['Unit'], fg='green', attrs='bold'))
                    print(''.join(print_list))

                elif dt['ObjType'] == 'BitField':
                    s_byte = dt['StartBit'] // 8
                    e_byte = s_byte + (dt['MaxBitSize'] // 8)
                    rv_str, pv_str = self._did_format(dt, Data)
                    SubData = Data[s_byte:e_byte]
                    print_list = []
                    print_list.append(' ' * indent)
                    print_list.append(color.format(dt['Name'], fg='green', attrs='bold'))
                    print_list.append('-')
                    print_list.append(color.format(rv_str, fg='blue', attrs='bold'))
                    print_list.append('-')
                    print_list.append(color.format(pv_str, fg='yellow', attrs='bold'))
                    print_list.append(' ')
                    print_list.append(color.format(dt['Unit'], fg='green', attrs='bold'))
                    print(''.join(print_list))
                    indent += 4
                    for pk in dt['PackList']:
                        rv_str, pv_str = self._did_bitFieldFormat(pk, SubData)
                        print_list = []
                        print_list.append(' ' * indent)
                        print_list.append(color.format(dt['Name'], fg='green', attrs='bold'))
                        print_list.append('-')
                        print_list.append(color.format(rv_str, fg='blue', attrs='bold'))
                        print_list.append('-')
                        print_list.append(color.format(pv_str, fg='yellow', attrs='bold'))
                        print_list.append(' ')
                        print_list.append(color.format(dt['Unit'], fg='green', attrs='bold'))
                        print(''.join(print_list))
                    indent -= 4
                else:
                    cprint('%s-%s' % (' '.join(['%02X' % (x) for x in Data]), ''.join([chr(x) for x in Data])), fg='green', attrs='bold')
        else:
            cprint('%s-%s' % (' '.join(['%02X' % (x) for x in Data]), ''.join([chr(x) for x in Data])), fg='green', attrs='bold')

    def _did_bitFieldFormat(self, dt, Data):
        v = int.from_bytes(Data, byteorder='big',signed=False)
        mask = 2 ** dt['MaxBitSize'] - 1
        rv = (v >> dt['StartBit']) & mask
        pv = self._did_phyValue(rv, dt)
        rv_str = '%02X'%(rv)
        pv_str = pv
        return rv_str, pv_str

    def _did_format(self, dt, Data):
        s_byte = dt['StartBit'] // 8
        bl = dt['MaxBitSize'] // dt['Segments']
        e_byte = s_byte + (bl // 8)
        rv_list = []
        pv_list = []
        for i in range(dt['Segments']):
            rv = int.from_bytes(Data[s_byte:e_byte], byteorder=dt['ByteOrder'], signed=dt['Signed'])
            pv = self._did_phyValue(rv, dt)
            rv_list.append(rv)
            pv_list.append(pv)
            s_byte = e_byte
            e_byte = s_byte + (bl // 8)
        sep = ','
        if dt['PhyType'] == 'ASCII':
            sep = ''
        pv_str = sep.join(pv_list)
        rv_str = ' '.join(['%02X'%(x) for x in rv_list])
        return rv_str, pv_str

    def _did_phyValue(self, rv, dt):
        if dt['PhyType'] == 'HEX':
            pv = "0x%02X"%(rv)
        elif dt['PhyType'] == 'ASCII':
            pv = chr(rv)
        elif dt['PhyType'] == 'DEC':
            pv = str(rv)
        elif dt['PhyType'] == 'BCD':
            pv = "%02X" % (rv)
        elif dt['PhyType'] == 'ENUM':
            pv = dt['SubObj'].get(rv, 'Unknown Value')
        elif dt['PhyType'] == 'LINEAR':
            fmt  = '{:0.%df}'%(dt['SubObj']['DecimalPlaces'])
            f = dt['SubObj']['Factor']
            d = dt['SubObj']['Divisor']
            o = dt['SubObj']['Offset']
            pv = fmt.format((rv * f / d) +o)
        else:
            pv = "0x%02X" % (rv)
        return pv

    def __call__(self, did, Data):
        self._did_print(did, Data)

def DTCFaultConfigLoad(excel_path):
    pick_config = None
    is_update = False
    try:
        with open(dtc_fault_pickle_path, 'rb') as f:
            pick_config = pickle.load(f)
        if os.path.exists(excel_path):
            excel_info = os.stat(excel_path)
            if int(pick_config['excel_mtime']) != int(excel_info.st_mtime):
                is_update = True
    except:
        is_update = True
    finally:
        if is_update:
            try:
                excel_info = os.stat(excel_path)
                config = GetDTCFaultConfig(excel_path)
                pick_config = dict(excel_mtime=excel_info.st_mtime,config=config)
                with open(dtc_fault_pickle_path, 'wb+') as f:
                    pickle.dump(pick_config, f, pickle.HIGHEST_PROTOCOL)
                return config
            except:
                cprint('can not load dtc config from:%s' % (excel_path), fg='red', attrs='bold')
                return None
        else:
            return pick_config['config']

def GetDTCFaultConfig(excel_path):
    dtc_sheet = 'ACCT DTCs'
    fault_sheet = 'ACCT Autoliv Faults'
    dtc_cols = [0, 1, 2, 3]
    fault_cols = [0, 3, 5, 6, 20]
    config = EJ(excel_path)
    dtc_json = config.GetSheetJsonByCols(dtc_sheet, *dtc_cols, start_row=1)
    fault_json = config.GetSheetJsonByCols(fault_sheet, *fault_cols, start_row=4)
    config.work_book_close()
    DTCs = {}
    for d in dtc_json:
        if d[0] != '' and d[1] != '':
            dtc = EJ.try_to_value('0x{:0>4s}{:0>2s}'.format(d[0], d[1]))
            DTCs[dtc] = (d[2],d[3])
    Faults = {}
    for f in fault_json:
        event_id = EJ.try_to_value(f[3])
        if f[5] != '' and f[6] !='':
            dtc = EJ.try_to_value('0x{:0>4s}{:0>2s}'.format(f[5], f[6]))
            Faults[event_id] = (dtc, f[0], f[20])
    return DTCs, Faults

def InternalFaultParser(DataRecord):

    def InternalFaultPrint(event_list):
        fault_info = dtc_fault_config[1]
        print_list = []
        HeaderFmt = "{:<8s}|{:<12s}|{:<12s}|{:<48s}|{:<12s}|{:<4s}"
        BodyFmt = "{:^8d}|{:<12d}|{:0>6X}      |{:<48s}|{:<12s}|{:0>2X}  "
        col_name = ('No.', "EventID", "DTC", "Event Name", "Status", "Hex Status")
        col_ctl = dict(fg=None, bg='yellow', attrs=None)
        for n, event in enumerate(event_list, start=1):
            e_info = fault_info.get(event[0], (0xFFFFFF, 'unknown','unknown'))
            status = DTC_STATUS.get(event[1] & 0x09, UNKNOWN_STATUS)
            ctl = dict(zip(('fg','bg','attrs'),status[1:]))
            text = (n, event[0], e_info[0], e_info[1], status[0], event[1])
            print_list.append(dict(ctl=ctl,text=text))
        cprint(HeaderFmt.format(*col_name), **col_ctl)
        #cprint('_'*90)
        for t in print_list:
            cprint(BodyFmt.format(*t['text']), **t['ctl'])

    event_list=[]
    for i in range(0, len(DataRecord), 3):
        event_id = (DataRecord[i] << 8) + DataRecord[i + 1]
        status = DataRecord[i + 2]
        if event_id != 0 and status != 0:
            event_list.append((event_id, status))
    InternalFaultPrint( event_list)

DID_Print_Func = {
    0xFD39: InternalFaultParser,
}

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
            if resp and resp.RespSID == 0x62 and resp.DID:
                cprint("%s:%s" % (resp_addr, resp_value),
                       fg=color, attrs='bold')
                if resp.DID in DID_Print_Func:
                    DID_Print_Func[resp.DID](bytes(resp.DataRecord))
                elif resp.DID in cdd_did_print:
                    cdd_did_print(resp.DID, resp.DataRecord)
            else:
                cprint("%s:%s" % (resp_addr, resp_value), fg=color, attrs='bold')
                if resp and resp.IsPositiveResponse and resp.RespSID == 0x62 and resp.DID in ASCII_DID_LIST:
                    cprint("".join(chr(x) for x in resp.DataRecord), fg='cyan', attrs='bold')
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

    def __init__(self,diag, wake_msg, keygen=None):
        self.wake_msg = wake_msg
        self.diag = diag
        self.keygen = keygen
        self.test_th = None

    def GetSecurityKey(self, seed_level, seed):
        if self.keygen is not None:
            key = self.keygen(seed_level, seed)
            if key is not None:
                return key[:len(seed)]
            else:
                return [0]*len(seed)
        else:
            return seed

    def UdsUnlock(self, level, diag=None):
        if diag is None:
            diag = self.diag
        resp = diag.SecurityAccess(level, IsCheck=False)
        if resp and resp.DataRecord and resp.DataRecord != [0x00]*(len(resp.DataRecord)):
            key = self.GetSecurityKey(level, resp.DataRecord)
            if key is not None:
                resp = diag.SecurityAccess(level + 1, *key, IsCheck=False)
        else:
            cprint('Unlock failed', fg='red',attrs='bold');
        return resp

    def DTCUnpack(self, DataRecord):
        dtc_list = []
        for i in range(0, len(DataRecord), 4):
            dtc = (DataRecord[i] << 16) + (DataRecord[i + 1]<<8) + DataRecord[i + 2]
            status = DataRecord[i + 3]
            dtc_list.append((dtc, status))
        return dtc_list
        
    def ReadDTCs(self, status='89'):
        self.diag.diagDelay(1)
        status=status.lower()
        if not status.startswith('0x'):
            status = '0x' + status
        status = int(status, 16)
        resp = self.diag.ReadDtcInformation(0x02, status, IsCheck=True)
        dtc_list = self.DTCUnpack(resp.DataRecord[1:])
        self.DTCPrint(dtc_list)
        
    def DTCPrint(self, dtc_list):
        dtc_info = dtc_fault_config[0]
        print_list = []
        HeaderFmt = "{:<8s}|{:<12s}|{:<48s}|{:<12s}|{:<4s}"
        BodyFmt = "{:^8d}|{:0>6X}      |{:<48s}|{:<12s}|{:0>2X}  "
        col_name = ('No.', "DTC", "DTC Name", "Status", "Hex Status")
        col_ctl = dict(fg=None, bg='yellow', attrs=None)
        for n, dtc in enumerate(dtc_list, start=1):
            d_info = dtc_info.get(dtc[0], ('unknown', 'unknown'))
            status = DTC_STATUS.get(dtc[1] & 0x09, UNKNOWN_STATUS)
            ctl = dict(zip(('fg','bg','attrs'),status[1:]))
            text = (n, dtc[0], d_info[0], status[0], dtc[1])
            print_list.append(dict(ctl=ctl,text=text))
        cprint(HeaderFmt.format(*col_name), **col_ctl)
        #cprint('_'*78)
        for t in print_list:
            cprint(BodyFmt.format(*t['text']), **t['ctl'])

    def ReadInternalFaults(self):
        resp = self.diag.ReadDataByIdentifier(0xFD39, IsCheck=True)

    def ChangePhase(self, phase, diag=None):
        try:
            if diag is None:
                diag = self.diag
            phase = int(phase)
            diag.SessionControl(0x03, IsCheck=True)
            self.UdsUnlock(0x1,diag=diag)
            if phase in [0,1]:
                diag.RoutineControl(0x01, 0xF106, phase, IsCheck=True)
                diag.diagDelay(1)
                diag.RoutineControl(0x03, 0xF106, IsCheck=True)
            elif phase ==2:
                diag.RoutineControl(0x01, 0xFE06, phase, IsCheck=True)
                diag.diagDelay(1)
                diag.RoutineControl(0x03, 0xFE06, IsCheck=True)
            diag.diagDelay(1)
            diag.ReadDataByIdentifier(0xFD63, IsCheck=True)
            print('Phase of life update Success!')
        except UdsResponseError as e:
            print(e)

    def general_keys_update(self, phy_tester, cid=1):
        #inject general keys
        for key_id in range(2, 21):
            phy_tester.SessionControl(0x03)
            self.UdsUnlock(0x1,diag=phy_tester)
            # power mode == OFF and MEC>0 and Normal communication disabled
            phy_tester.diagRawRequest(0x28, 0x03, 0x03)
            key_name = "KEY_%d" % key_id
            # cid shall big than the cid in ECU
            key = ProvisionKey(KeyName=key_name, Cid=cid, NewKey=[0x00] * 16)
            key.Generate()
            rid_frame = bytes([0x31,0x01,0x02,0x72,key_id])+key.M1+key.M2+key.M3
            resp = phy_tester.diagRawRequest(*rid_frame)
            pv_state = resp.DataRecord[0]
            if pv_state == 0:
                cprint('general Key provision successful[slot=%d]'%(key_id), fg='blue', attrs='bold')
            else:
                cprint('general Key provision failed[slot=%d, state=0x%02X]'%(key_id, pv_state), fg='red', attrs='bold')

    def PATAC_keys_update(self, phy_tester):
        #update PATAC fixed keys
        phy_tester.SessionControl(0x03)
        self.UdsUnlock(0x1,diag=phy_tester)
        # power mode == OFF and MEC>0 and Normal communication disabled
        phy_tester.diagRawRequest(0x28, 0x03, 0x03)
        PATAC_ECU_UNLOCK_KEY_M1M2M3 = [0x00]*15 + [0x44]+[0x1b,0xaf,0xa3,0xb9,0x5a,0x64,0xdf,0x9b,0x40,0xb8,0xfd,0x17,0xa4,0x74,0x33,0xe1,0x30,0x0e,0x17,0x06,0x22,0x0e,0x7b,0x5c,0xdc,0x2f,0x40,0x5c,0xc1,0x67,0x33,0x33,0x5a,0x64,0x16,0x4e,0x98,0x1a,0x4d,0x32,0xa1,0x34,0x9f,0x84,0x57,0x95,0xe0,0xbb]     
        PATAC_ECU_MASTER_KEY_M1M2M3 = [0x00]*15 + [0x11]+[0xa4,0xba,0x2f,0xee,0xcf,0x1a,0x77,0xbb,0x82,0x97,0xc3,0x89,0xe4,0xdd,0xcd,0x6b,0x37,0xbc,0x06,0xe8,0x05,0x8f,0xb3,0xcf,0x45,0x84,0xfa,0x81,0xee,0x43,0xea,0xeb,0x9c,0x69,0xef,0x33,0x1c,0x0c,0x02,0x02,0x57,0x11,0xde,0xa1,0x1b,0x4e,0x11,0xc2]
        #inject PATAC Ecu unlock key        
        rid_frame = bytes([0x31,0x01,0x02,0x72,0x01])+bytes(PATAC_ECU_UNLOCK_KEY_M1M2M3)
        resp = phy_tester.diagRawRequest(*rid_frame)
        pv_state = resp.DataRecord[0]
        if pv_state == 0:
            cprint('UNLOCK Key provision successful[slot=%d]' % (1), fg='blue', attrs='bold')
        else:
            cprint('UNLOCK Key provision failed[slot=%d, state=0x%02X]' % (1, pv_state), fg='red', attrs='bold')
        #inject PATAC master key
        phy_tester.SessionControl(0x03)
        self.UdsUnlock(0x1, diag=phy_tester)
        # power mode == OFF and MEC>0 and Normal communication disabled
        phy_tester.diagRawRequest(0x28, 0x03, 0x03)
        rid_frame = bytes([0x31,0x01,0x02,0x72,0xff])+bytes(PATAC_ECU_MASTER_KEY_M1M2M3)
        resp = phy_tester.diagRawRequest(*rid_frame)
        pv_state = resp.DataRecord[0]
        if pv_state == 0:
            cprint('Master Key provision successful[slot=%d]' % (0xff), fg='blue', attrs='bold')
        else:
            cprint('Master Key provision failed[slot=%d, state=0x%02X]' % (0xff, pv_state), fg='red', attrs='bold')

    def UdsCycleRead(self, did):
        pass

    def UdsCmdProcess(self):
        is_exit = False
        subparser = UdsArgumentParser(prog='uds', usage='This is the common diag cmd services', description='Please input diag services or following cmd', add_help=False).GetSubParser()
        subparser.Add_SubArgs('exit', help='quit the program')
        subparser.Add_SubArgs('quit', help='exit the program')
        subparser.Add_SubArgs('dtc', help='read dtc with mask status 0x89')
        subparser.Add_SubArgs('fault', help='read Veoneer Internal Fault')
        subparser.Add_SubArgs('start', help='Start Send TesterPresent')
        subparser.Add_SubArgs('stop', help='Stop Send TesterPresent')
        subparser.Add_SubArgs('unlock', subparser.SubArgObj('value', metavar='SubFunc of Unlock Level'), help='Unlock Security access')
        subparser.Add_SubArgs('phase', subparser.SubArgObj('value', type=int, metavar='0/1/2'), help='change to the target phase 0/1/2')
        subparser.Add_SubArgs('uds', subparser.SubArgObj('value', type=str, nargs='+', metavar='xx xx ...'), help='common diag services')
        subparser.Add_SubArgs('kp', subparser.SubArgObj('value', type=int, metavar='cid value'), help='Start key provision with cid, the cid shall big than the value in ECU')
        self.subparser = subparser
        cprint(subparser.format_help(), fg='green', attrs='bold')
        while not is_exit:
            try:
                is_exit = self._uds_cmd_process(self.diag)
            except Exception as e:
                cprint("%s: %s"%(type(e).__name__, e), fg='red', attrs='bold')


    def ReadAllDID(self):
        self.diag.diagDelay(2)
        for did in cdd_did_print:
            self.diag.ReadDataByIdentifier(did)
            self.diag.diagDelay(0.5)

    def GacClearDTC(self):
        self.diag.ClearDiagnosticInformation(0xFFFFFF, IsCheck=True)

    def _uds_cmd_process(self, diag):

        subparser = self.subparser
        cmds = input('$ ')
        try:
            p = subparser.ParseArgStr(cmds)
        except Exception:
            return False
        if cmds == '':
            cprint(subparser.format_help(), fg='green', attrs='bold')
        elif p.cmd in ('exit', 'quit'):
            diag.StopTesterPresent()
            return True
        elif p.cmd  == 'start':
            diag.StartTesterPresent()
            print('Start Send TesterPresent')
        elif p.cmd  == 'stop':
            diag.StopTesterPresent()
            print('Stop Send TesterPresent')
        elif p.cmd  == 'dtc':
            self.ReadDTCs()
        elif p.cmd  == 'fault':
            self.ReadInternalFaults()
        elif p.cmd == 'unlock':
            level = int('0x'+ p.value, 16)
            self.UdsUnlock(level, diag=diag)
        elif p.cmd == 'phase':
            phase = p.value
            self.ChangePhase(phase, diag=diag)
        elif p.cmd == 'kp':
            cid = p.value
            self.general_keys_update(diag, cid)
            self.PATAC_keys_update(diag)
        elif p.cmd == 'uds':
            for cmd in p.value:
                diag.diagRawRequest(*cmd)
        return False

def main(args):
    global dtc_fault_config
    global cdd_did_print
    config = Scripts.UdsConfigParse('UdsConfig.json')
    dtc_config_path = config.config['DTC'][0]['Path']
    cdd_did_path = config.config['Cdd']['Path']
    cdd_did_print = CddDidPrint(cdd_did_path)
    dtc_fault_config = DTCFaultConfigLoad(dtc_config_path)
    bus = config.GetBus('SGM458CAN')
    # diag = CmdUds(uds_client=config.GetUdsClient('CanPhy'))
    diag = config.GetUdsDiag('SGM458', diag_cls='CmdUds')
    key_gen = config.GetKeyGens("SGM458")
    wake_msg = config.GetMessage('NM_GM458')
    uds = GacUdsCom(diag, wake_msg, key_gen)
    Cmds = {
        "cleardtc": uds.GacClearDTC,
        'uds': uds.UdsCmdProcess,
        'dtc': uds.ReadDTCs,
        'fault': uds.ReadInternalFaults,
        'readalldid': uds.ReadAllDID
    }
    bus.set_filters([0x14DA58F1,0x10DBFEF1,0x14DAF158])
    with PyUds.ThreadSafety(bus):
        PyUds.MessageLog.start(log_level=PyUds.log.LOG_WRITE_FILE_MASK)
        try:
            wake_msg.start()
            bus.wait(0.5)
            Cmds[args[0]](*args[1:])
        except UdsResponseError as ex:
            print(ex)
            traceback.print_exc()
        except KeyError as ex:
            print(ex)
            print('Please input cmd in:', Cmds.keys())
            traceback.print_exc()
        except TypeError as ex:
            print(ex)
            print('Please input cmd in:', Cmds.keys())
            traceback.print_exc()
        except KeyboardInterrupt:
            if uds.test_th is not None:
                uds.test_th.join()
            diag.StopTesterPresent()
        finally:
            pass
            # wake_msg.stop()
            PyUds.MessageLog.stop()
        # PyUds.MessageLog.stop()

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

    if len(sys.argv) == 1:
        sys.argv.append('uds')
    if len(sys.argv) > 1:
        cmds = argv_process(sys.argv[1:])
        wk_path = os.path.join(os.path.dirname(__file__), 'GM458_scripts')
        if not os.path.exists(wk_path):
            bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
            wk_path = os.path.join(bundle_dir, 'GM458_scripts')
        os.chdir(wk_path)
        main(cmds)
