# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 13:11:34 2021

@author: levy.he
@file  : __init__.py
"""
import platform
from .SecurityKey import BaseKeyGen, InternalKeyGen, SecurityKeyGens
if platform.architecture()[0] == '64bit':
    from .DllKeyClient import DllKeyGen
else:
    from .SecurityKey import DllKeyGen
