# -*- coding: utf-8 -*-
"""
    Collection of simple blocks to make model development faster.
"""

from bms.blocks.continuous import ODE

class IntegrationBlock(ODE):
    """Creates an ODE block that performs integration of the input over time.

    .. math:: output = \int_{0}^{t} input\ dt

    Args:
        input_variable: This is the input or list of inputs of the block.
        output_variable (Variable): This is the output of the block.

    """
    def __init__(self, input_variable, output_variable):
        ODE.__init__(self, input_variable, output_variable, a=[1], b=[0, 1])
        
    def LabelBlock(self):
        return 'Integral'
    
class DifferentiationBlock(ODE):
    """Creates an ODE block that performs differentation of the input relative to time.
    
    .. math:: output = \\frac{d[input]}{dt}

    Args:
        input_variable: This is the input or list of inputs of the block.
        output_variable (Variable): This is the output of the block.

    """
    def __init__(self, input_variable, output_variable):
        ODE.__init__(self, input_variable, output_variable, a=[0, 1], b=[1])
        
    def LabelBlock(self):
        return 'dx/dt'
