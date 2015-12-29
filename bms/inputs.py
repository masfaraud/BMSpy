# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 14:24:23 2015

@author: steven
"""

from bms import *

class Step(Input):
    def __init__(self,value,name):
        Input.__init__(self,name)
        self.function=lambda x:value

class Ramp(Input):
    def __init__(self,value,name):
        Input.__init__(self,name)
        self.function=lambda x:x*value            