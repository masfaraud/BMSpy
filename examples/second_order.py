# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 18:42:33 2015

@author: steven
"""

import sys
sys.path.append('../')
import bms

K=1
Q=0.707
w0=7

e=bms.Step(4.,'e')
s=bms.Variable('s',[0])

block=bms.ODEBlock(e,s,[1],[1,2*Q/w0,1/w0**2])
ds=bms.DynamicSystem(4,60,[block])
#res=ds.ResolutionOrder()
#print(res)
ds.Simulate()
ds.PlotVariables()