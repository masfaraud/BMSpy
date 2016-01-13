# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 18:22:42 2015

@author: steven
"""

import bms
from bms.inputs.wltp import WLTP3
from bms.blocks.continuous import Gain

Vc=WLTP3('WLTP Cycle')
V=bms.Variable('Speed')
block=Gain(Vc,V,1)
ds=bms.DynamicSystem(450,5000,[block])
ds.Simulate()
ds.PlotVariables([[Vc]])