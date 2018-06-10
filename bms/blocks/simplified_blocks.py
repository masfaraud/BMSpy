# -*- coding: utf-8 -*-
"""
    Collection of simple blocks to make model development faster.
"""

from bms.blocks.continuous import ODE

class IntegrationBlock(ODE):
    """
        Creates an ODE block that performs integration over time.
    """
    def __init__(self, input_variable, output_variable):
        ODE.__init__(self, input_variable, output_variable, a=[1], b=[0, 1])
        
    def LabelBlock(self):
        return 'Integral'
    
class DifferentiationBlock(ODE):
    """
        Creates an ODE block that performs differentation relative to time.
    """
    def __init__(self, input_variable, output_variable):
        ODE.__init__(self, input_variable, output_variable, a=[0, 1], b=[1])
        
    def LabelBlock(self):
        return 'dx/dt'
