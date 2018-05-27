# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 18:42:33 2015

@author: steven
"""

import bms
from bms.signals.functions import Sinus
from bms.blocks.continuous import ODE

K = 1
Q = 0.3
w0 = 3

# e=bms.Step('e',4.)
e = Sinus('e', 4., 5)
s = bms.Variable('s', [0])

block = ODE(e, s, [1], [1, 2*Q/w0, 1/w0**2])
ds = bms.DynamicSystem(5, 200, [block])

# ds.DrawModel()
ds.Simulate()
ds.PlotVariables()
