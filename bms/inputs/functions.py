# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 14:24:23 2015

@author: steven
"""

from bms import *
from math import sin

class Step(Input):
    def __init__(self,name='Step',amplitude=1,delay=0,initial_value=0):
        Input.__init__(self,name)
        def function(t):
            if t<delay:
                return initial_value
            else:
                return amplitude+initial_value
        self.function=function

class Ramp(Input):
    def __init__(self,name='Ramp',amplitude=1,delay=0,initial_value=0):
        Input.__init__(self,name)
        def function(t):
            if t<delay:
                return initial_value
            else:
                return (t-delay)*amplitude+initial_value
        self.function=function        
        
class Sinus(Input):
    def __init__(self,name='Sinus',amplitude=1,w=1,phase=0,initial_value=0):
        Input.__init__(self,name)
        self.function=lambda t:amplitude*sin(w*t+phase)+initial_value
    
class InputFunction(Input):
    def __init__(self,name,function):
        Input.__init__(self,name)
        self.function=function


