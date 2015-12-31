# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 18:22:42 2015

@author: steven
"""

import bms

Vc=bms.WLTP3('WLTP Cycle')
V=bms.Variable('Speed')
block=bms.Gain(Vc,V,1)
ds=bms.DynamicSystem(20,20,[block])
ds.Simulate()
ds.PlotVariables()