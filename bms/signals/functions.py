# -*- coding: utf-8 -*-

"""
Collection of mathematical function signals
"""

from bms import Signal
from math import sin

class Step(Signal):
    """
        Create a Step of amplitude beginning at time delay
    """
    def __init__(self,name='Step',amplitude=1,delay=0,offset=0):
        Signal.__init__(self,name)
        def function(t):
            if t<delay:
                return offset
            else:
                return amplitude+offset
        self.function=function

class Ramp(Signal):
    """
        Create a ramp such as : f(t)=(t-delay)*amplitude+initial_value
    """
    def __init__(self,name='Ramp',amplitude=1,delay=0,offset=0):
        Signal.__init__(self,name)
        def function(t):
            if t<delay:
                return offset
            else:
                return (t-delay)*amplitude+offset
        self.function=function        
        
class Sinus(Signal):
    def __init__(self,name='Sinus',amplitude=1,w=1,phase=0,offset=0):
        Signal.__init__(self,name)
        self.function=lambda t:amplitude*sin(w*t+phase)+offset
    
class SignalFunction(Signal):
    """
        User defined function for signal.
        
        :param function: a function that will give the time values to the signal
    """
    def __init__(self,name,function):
        Signal.__init__(self,name)
        self.function=function

