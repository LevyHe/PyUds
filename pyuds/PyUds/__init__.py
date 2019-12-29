# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 11:01:35 2019

@author: levy.he
"""

from .bus import Message, CanBus, CanFdBus
from .bus import FrFrame, FrBus
from .CanTp import CanTp, CanFdTp
from .FrTp import FrTp
from .ComBase import ComCan, ComCanFd, ComFr, Sender, Receiver, ComBase, BusBase, TpBase, ThreadSafety
from .UdsBase import DiagRequest, DiagResponse, DiagClient, BaseDiagnostic
from .MsgManage import DBPaser, DBMessage, DBMsgReader, DBMsgSender, DBMsgReadOnce, DBMsgSendOnce, CanMsgSendOnce, CanMsgReadOnce, CanMsgReader, CanMsgSender
from .FrameManage import FrSendOnce, FrReadOnce, FrReader, FrSender, FrTimeSender
from . import wres
from .log import MessageLog

class CanPeriodSender(Sender):

    def __init__(self, can_id, data, period=1.0, channel=None):
        if can_id > 0x7FF:
            ext_id = True
            can_id &= 0x1FFFFFFF
        else:
            ext_id = False
            can_id &= 0x7FF
        msg = Message(arbitration_id=can_id, data=data, channel=channel, is_extended_id=ext_id)
        super(CanPeriodSender, self).__init__(period, msg)

    def update_msg(self, can_id, data, channel=None):
        if can_id > 0x7FF:
            ext_id = True
            can_id &= 0x1FFFFFFF
        else:
            ext_id = False
            can_id &= 0x7FF
        msg = Message(arbitration_id=can_id, data=data, channel=channel, is_extended_id=ext_id)
        self.__msg = msg


class CanCycleReader(Receiver):

    def __init__(self, can_id):
        if can_id > 0x7FF:
            self.is_extended_id = True
            self.arbitration_id = can_id & 0x1FFFFFFF
        else:
            self.is_extended_id = False
            self.arbitration_id &= can_id & 0x7FF

    def reader(self, msg):
        pass

    def __call__(self, msg):
        if msg.is_extended_id == self.is_extended_id and msg.arbitration_id == self.arbitration_id:
            self.reader(msg)

