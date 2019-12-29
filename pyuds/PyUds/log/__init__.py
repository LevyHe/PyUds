# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 19:38:46 2019

@author: levy.he
"""
import time
import os
from functools import wraps, partial
from .. import Message, FrFrame

MSG_LIST = (Message, FrFrame)

LOG_WRITE_FILE_MASK = 0x04
LOG_PRINT_MASK = 0x02
LOG_LIST_MASK = 0x01

class MessageLog(object):


   
    def __init__(self):
        self.file = None
        self.log_level = 0
        self.log_list = []
        self.log_start_time = time.time()

    def __call__(self, func):
        @wraps(func)
        def caller(*args, **kwargs):
            if len(args) > 1:
                msg_format = args[0].msg_format
                log_filters = None
                if hasattr(args[0], 'log_filters'):
                    log_filters = args[0].log_filters
                tx_msg = args[1]
                rx_msg = func(*args, **kwargs)
                if self.log_level > 0:
                    log_msg = tx_msg if isinstance(tx_msg, MSG_LIST) else rx_msg
                    if isinstance(log_msg, MSG_LIST) and log_filters(log_msg):
                        self.msg_log(msg_format(log_msg))
            return rx_msg
        return caller

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    def msg_log(self, msg):
        if self.log_level & LOG_LIST_MASK == LOG_LIST_MASK:
            self.log_list.append(msg)
        if self.log_level & LOG_PRINT_MASK == LOG_PRINT_MASK:
            print(msg)
        if self.log_level & LOG_WRITE_FILE_MASK == LOG_WRITE_FILE_MASK:
            self.file.write(msg+'\n')

    def get_logs(self):
        return self.log_list

    def start(self, file=None, log_level=1):
        self.log_level=log_level
        self.log_list = []
        if self.log_level & LOG_WRITE_FILE_MASK == LOG_WRITE_FILE_MASK:
            if hasattr(file, 'write'):
                self.file = file
            elif self.file is None:
                if not os.path.exists('Log'):
                    os.makedirs('Log')
                file_name = r'Log\Log' + \
                    time.strftime('_%Y%m%d%H%M%S',
                                  time.localtime(time.time()))+'.asc'
                self.file = open(file_name, 'w+')
                self.file.write('Date ' + time.asctime(time.localtime(time.time())) + '\n')
    
    def stop(self):
        self.log_level = 0
        if self.file is not None:
            self.file.close()
            self.file=None

MessageLog = MessageLog()
