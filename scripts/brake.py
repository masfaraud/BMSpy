#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:04:22 2017

@author: steven
"""

import bms
from bms.signals.functions import Step, Sinus
from bms.blocks.continuous import Gain, ODE, Sum, Subtraction, Product, WeightedSum
from bms.blocks.nonlinear import CoulombVariableValue, Saturation, Coulomb

Cmax = 300  # Max clutch torque handling
I1 = 1
I2 = 0.25
fv1 = 0.01
fv2 = 0.01
# e=bmsp.Step(1.,'e')

cc = Sinus(('Brake command', 'cc'), 0.5, 0.1, 0, 0.5)
it = Step(('Input torque', 'it'), 100)
rt = Step(('Resistant torque', 'rt'), -80)

tc = bms.Variable(('brake Torque capacity', 'Tc'))
bt = bms.Variable(('brake torque', 'bt'))
w1 = bms.Variable(('Rotational speed shaft 1', 'w1'))
#dw12=bms.Variable(('Clutch differential speed','dw12'))
st1 = bms.Variable(('Sum torques on 1', 'st1'))
et1 = bms.Variable(('Sum of ext torques on 1', 'et1'))


b1 = Gain(cc, tc, Cmax)
b2 = WeightedSum([it, rt], et1, [1, 1])
b3 = CoulombVariableValue(et1, w1, tc, bt, 0.1)
# b3=Coulomb(it,dw12,ct,150)

b4 = ODE(st1, w1, [1], [fv1, I1])
# b5=ODE(st2,w2,[1],[fv2,I2])
b6 = WeightedSum([it, rt, bt], st1, [1, 1, 1])
# b7=WeightedSum([it,rt],et1,[1,1])

ds = bms.DynamicSystem(100, 400, [b1, b2, b3, b4, b6])


# ds.DrawModel()
r = ds.Simulate()
ds.PlotVariables([[w1], [tc, bt, rt, it, st1, et1]])
import matplotlib.pyplot as plt
plt.figure()
plt.plot(r)
plt.show()
# ds.PlotVariables([[cc]])
