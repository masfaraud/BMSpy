# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:52:02 2016

@author: steven
"""

import bms
from bms.signals.functions import Step
from bms.blocks.continuous import Gain, ODE, Sum, Subtraction, Product


Ka = 3
Kb = 4
Kc = 3
tau = 1

I = Step(('input', 'i'), 100.)
AI = bms.Variable(('adapted input', 'ai'), [100.])
dI = bms.Variable(('error', 'dI'))
O = bms.Variable(('Output', 'O'))
F = bms.Variable(('Feedback', 'F'))

b1 = Gain(I, AI, Ka)
b2 = Subtraction(AI, F, dI)
b3 = ODE(dI, O, [Kb], [1, tau])
b4 = Gain(O, F, Kc)

ds = bms.DynamicSystem(3, 1000, [b1, b2, b3, b4])
r = ds.Simulate()
ds.PlotVariables([[I, O, dI, F]])


# I2=Step(('input','i'),100.)
#O2=bms.Variable(('Output','O'))#
# ds2=bms.DynamicSystem(3,600,[ODE(I2,O2,[Ka*Kb],[1+Kc*Kb,tau])])
# ds2.Simulate()
# ds2.PlotVariables()
