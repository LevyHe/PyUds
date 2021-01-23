# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 00:09:10 2021

@author: levy.he
@file  : DllKeyServer.py
"""
# if __name__ == "__main__":
#     import sys
#     import importlib
#     from pathlib import Path

#     def import_parents(level=1):
#         global __package__
#         file = Path(__file__).resolve()
#         parent, top = file.parent, file.parents[level]

#         sys.path.append(str(top))
#         try:
#             sys.path.remove(str(parent))
#         except ValueError:  # already removed
#             pass

#         __package__ = '.'.join(parent.parts[len(top.parts):])
#         importlib.import_module(__package__)  # won't be needed after that
#     import_parents(1)

# from .DllKeyClient import DllKeyGenBase
from ProxyManager import ProxyManager, ServerForever, err_print
from SecurityKey import DllKeyGen

class DllKeyProxy(ProxyManager):
    pass


DllKeyProxy.register('DllKeyGen', DllKeyGen)

if __name__ == "__main__":
    print = err_print
    ServerForever(DllKeyProxy)
