# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 10:44:04 2019

@author: levy.he
"""

from pyuds import Scripts
if __name__ == '__main__':
    config = Scripts.UdsConfigParse('UdsConfig.json')
    fr_sample = config.GetMessage('FrSample')
    print(fr_sample)