#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 13:00:09 2021

@author: levy.he
@file  : dllkey_test.py
"""
import os
import time
from pyuds.Scripts import DllKeyGen


if __name__ == '__main__':
    dll_path = "uds_test.dll"
    dll_path = os.path.abspath(dll_path)
    
    key_gen1 = DllKeyGen(0x01, dll_path=dll_path)
    key_gen2 = DllKeyGen(0x011, dll_path=dll_path)
    seed = os.urandom(4)
    key1 = key_gen1.KenGen(1, seed)
    key2 = key_gen2.KeyGen(0x11, seed)
    print(key1,key2)
    time.sleep(10)
