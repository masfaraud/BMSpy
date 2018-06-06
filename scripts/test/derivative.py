#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 09:54:28 2017

@author: steven
"""

import bms
from bms.signals.functions import Step, Sinus
from bms.blocks.continuous import Gain, ODE, Sum, Subtraction, Product, WeightedSum


Ka = 3
Kb = 4
Kc = 3
tau = 1
#
# I=Step(('input','i'),100.)
#AI=bms.Variable(('adapted input','ai'),[100.])
# dI=bms.Variable(('error','dI'))
#O=bms.Variable(('Output','O'))#
#F=bms.Variable(('Feedback','F'))#
#
# b1=Gain(I,AI,Ka)
# b2=Subtraction(AI,F,dI)
# b3=ODE(dI,O,[Kb],[1,tau])
# b4=Gain(O,F,Kc)
#
# ds=bms.DynamicSystem(3,1000,[b1,b2,b3,b4])
# ds.Simulate()
# ds.PlotVariables([[I,O,dI]])

# ==============================================================================
#  Computation of the derivative of sinus
# ==============================================================================

# I2=Sinus(('input','i'),100.)
#O2=bms.Variable(('Output','O'))#
# b=ODE(I2,O2,[0,1],[1])
# ds2=bms.DynamicSystem(15,3000,[b])
# ds2.Simulate()
# ds2.PlotVariables()

# print(b.Mi,b.Mo)
# print()

# ==============================================================================
#  Feedback with derivative for stability test
# ==============================================================================

I = Step(('input', 'i'), 100.)
AI = bms.Variable(('adapted input', 'ai'), [100.])
dI = bms.Variable(('error', 'dI'))
O = bms.Variable(('Output', 'O'))
F = bms.Variable(('Feedback', 'F'))

b1 = Gain(I, AI, Ka)
b2 = WeightedSum([AI, dI], F, [1, -1])
b3 = ODE(O, dI, [1, tau], [Kb])
b4 = Gain(F, O, 1/Kc)
#
# ds.
ds = bms.DynamicSystem(0.1, 20, [b1, b2, b3, b4])
ds.Simulate()
ds.PlotVariables([[I, O, dI, F]])
