# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 00:08:58 2021

@author: levy.he
@file  : DllKeyClient.py
"""
import os
import platform
import struct
from .ProxyManager import ProxyManager, ServerClient
from .SecurityKey import BaseKeyGen
from .SecurityKey import DllKeyGen as DllKeyGenBase
if platform.architecture()[0] == '64bit':
    is_64bit = True
else:
    is_64bit = False

class DllFileError(Exception):
    pass

def arch_type(dll_file):
    with open(dll_file, 'rb') as f:
        doshdr = f.read(64)
        magic, padding, offset = struct.unpack('2s58si', doshdr)
        if magic != b'MZ':
            return None
        f.seek(offset, os.SEEK_SET)
        pehdr = f.read(6)
        magic, padding, machine = struct.unpack('2s2sH', pehdr)
        if magic != b'PE':
            return None
        archs = {0x014c: 'i386', 0x0200: 'IA64', 0x8664: 'x64'}
        return archs.get(machine, 'unknown')

if is_64bit:
    class DllKeyProxy(ProxyManager):
        pass

    DllKeyProxy.register('DllKeyGen', DllKeyGenBase)

    class DllKeyGen_x32(object):
        _proc = None
        _proxy = None
        def __init__(self, *seed_levels, dll_path=None):
            if dll_path:
                self.dll_path = dll_path
                self.seed_levels = seed_levels
                if __class__._proc is None or __class__._proxy is None:
                    server_exe = os.path.join(os.path.dirname(__file__),'DllKeyServer_32bit.exe')
                    cmd = [server_exe]
                    _proc, _proxy = ServerClient(cmd, DllKeyProxy)
                    __class__._proc, __class__._proxy = _proc, _proxy
                else:
                    _proc, _proxy = __class__._proc, __class__._proxy
                self._keygen = self._proxy.DllKeyGen(*seed_levels, dll_path=self.dll_path)
                
            else:
                self.seed_levels=[]

        def KeyGen(self, level, seed):
            if level in self.seed_levels:
                return self._keygen.KeyGen(level, seed)
            else:
                return seed

        @staticmethod
        def at_exit():
            if __class__._proc:
                __class__._proc.stdout.close()
                __class__._proc.stdin.close()
                __class__._proc.kill()


    class DllKeyGen(BaseKeyGen):

        def __init__(self, *seed_levels, dll_path=None):
            arch = arch_type(dll_path)
            if arch == 'i386':
                import atexit
                atexit.register(DllKeyGen_x32.at_exit)
                gen_type = DllKeyGen_x32
            elif arch == 'x64':
                gen_type = DllKeyGenBase
            else:
                raise DllFileError(f'A not supported dll type [{arch}]')
            self.keygen = gen_type(*seed_levels, dll_path=dll_path)

        def KeyGen(self, level, seed):
            return self.keygen.KeyGen(level, seed)
else:
    DllKeyGen = DllKeyGenBase


