# -*- coding: utf-8 -*-
"""
    Collection of simple functions to make model development faster.
"""

from bms.signals.functions import Ramp

class Time(Ramp):
    """Creates a Ramp that is equal to the time variable of the simulation.

    .. math:: f(t) = t

    Args:
        name (str): The name of this signal.
        
    """
    def __init__(self):
        Ramp.__init__(self, name='time', amplitude=1)
    
    def LabelBlock(self):
        return 't'