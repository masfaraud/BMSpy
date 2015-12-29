# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 18:34:19 2015

@author: Steven Masfaraud
"""

import bms

K=1.
tau=1.254

#e=bmsp.Step(1.,'e')
e=bms.Ramp(1.,'e')
s=bms.Variable([0],'s')

block=bms.ODE(e,s,[K],[1,tau])
ds=bms.DynamicSystem(10,100,[block])
#res=ds.ResolutionOrder()
#print(res)
ds.Simulate()
#ds.PlotVariables()

## External plot for verification
import matplotlib.pyplot as plt
plt.figure()
plt.plot(ds.t,e.values)
plt.plot(ds.t,s.values)
s_inf=K*(ds.t.copy()-tau)
plt.plot(ds.t,e.values)
plt.plot(ds.t,s_inf)

