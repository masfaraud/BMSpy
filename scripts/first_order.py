# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 18:34:19 2015

@author: Steven Masfaraud
"""

import bms
from bms.signals.functions import Ramp
from bms.blocks.continuous import ODE

K = 1.
tau = 1.254

# e=bms.Step('e',1.)
e = Ramp('e', 1.)
s = bms.Variable('s', [0])

block = ODE(e, s, [K], [1, tau])
ds = bms.DynamicSystem(10, 100, [block])
# res=ds.ResolutionOrder()
# print(res)
ds.Simulate()
# ds.PlotVariables()

# ds.DrawModel()

# External plot for verification
import matplotlib.pyplot as plt
plt.figure()
plt.plot(ds.t, e.values)
plt.plot(ds.t, s.values)
s_inf = K*(ds.t.copy()-tau)
plt.plot(ds.t, e.values)
plt.plot(ds.t, s_inf)
