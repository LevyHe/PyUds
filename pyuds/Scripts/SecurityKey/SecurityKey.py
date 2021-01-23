# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 22:16:28 2019

@author: levy.he
"""

import ctypes

KEY_ARRAY_SIZE=64
c_byte_a = ctypes.c_char_p
c_size = ctypes.c_uint32
c_level = ctypes.c_uint32
c_buf = ctypes.c_char * KEY_ARRAY_SIZE
rtn_status = ctypes.c_int


class BaseKeyGen(object):
    def __init__(self, *seed_levels):
        self.seed_levels = list(seed_levels)

    def KeyGen(self, level, seed):
        return seed

    def KenGen(self, level, seed):
        return self.KeyGen(level, seed)

    def __call__(self, level, seed):
        return self.KeyGen(level, seed)

class DllKeyGen(BaseKeyGen):

    def __init__(self, *seed_levels, dll_path=None):
        self.dll_path = dll_path
        if dll_path is not None:
            self.seed_levels = seed_levels
            self.dll = ctypes.cdll.LoadLibrary(dll_path)
            try:
                self.GenerateKeyEx = self.dll.GenerateKeyEx
                self.GenerateKeyEx.argtypes = [c_byte_a, c_size, c_level, c_byte_a, c_byte_a, c_size, ctypes.POINTER(c_size)]
                self.dll_type = 'Basic'
            except:
                self.GenerateKeyEx = self.dll.GenerateKeyExOpt
                self.GenerateKeyEx.argtypes = [c_byte_a, c_size, c_level, c_byte_a, c_byte_a, c_byte_a, c_size, ctypes.POINTER(c_size)]
                self.dll_type = 'Opt'
            
            self.GenerateKeyEx.restype = rtn_status
        else:
            self.seed_levels = []
    
    def KeyGen(self, level, seed):
        if self.dll_path is None:
            return None
        key = c_buf()
        _seed = c_buf(*seed)
        key_out_size = c_size(0)
        varint = ''
        if self.dll_type == 'Opt':
            rtn = self.GenerateKeyEx(_seed, len(seed), level, varint.encode(
                'ascii'), varint.encode('ascii'), key, KEY_ARRAY_SIZE, ctypes.byref(key_out_size))
        else:
            rtn = self.GenerateKeyEx(_seed, len(seed), level, varint.encode(
                'ascii'), key, KEY_ARRAY_SIZE, ctypes.byref(key_out_size))
        if rtn == 0:
            key = key[0:key_out_size.value]
            return list(key)
        else:
            return None

class InternalKeyGen(BaseKeyGen):
    def KeyGen(self, level, seed):
        if level not in self.seed_levels:
            return None
        return [(~x) & 0xFF for x in seed]

        
class LE45PKeyGen(BaseKeyGen):
    M_U16_SECURITY3_DATA = 0x239A
    '''supported seed level is 0x7d'''
    def KeyGen(self, level, seed):
        if level not in self.seed_levels:
            return None
        cu16Data = self.M_U16_SECURITY3_DATA
        cu16Seed = ((seed[0] << 8) + seed[1]) & 0xFFFF
        u16TempKey = (((((cu16Seed >> 8) ^ (cu16Seed & 0x00FF)) ^
                        (cu16Data >> 8)) ^ (cu16Data & 0x00FF))) & 0xFFFF
        u16TempKey += cu16Data
        return [(u16TempKey >> 8) & 0xFF, u16TempKey & 0xFF]


class SecurityKeyGens(BaseKeyGen):

    def __init__(self, *gens):
        self.gen_list = list(gens)

    def add_key_gen(self, gen):
        self.gen_list.append(gen)

    def KeyGen(self, level, seed):
        for gen in self.gen_list:
            if level in gen.seed_levels:
                return gen(level, seed)
        return None
        

if __name__ == '__main__':
    dll_name = "uds_test.dll"
    key_gen = DllKeyGen(0x01,0x11, dll_path=dll_name)
    int_key_gen = InternalKeyGen(0x61)
    skey = SecurityKeyGens(key_gen, int_key_gen)
    keys = skey([0x12, 0x32, 0x31, 0x50], 0x01)
    int_kyes = skey([0x12, 0x32, 0x31, 0x50], 0x61)
    print(["%02X"%(x) for x in keys])
    print(["%02X"%(x) for x in int_kyes])
