#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 13:20:15 2017

@author: steven
"""

import bms
from bms.signals.functions import Step, Sinus
from bms.blocks.continuous import Gain, ODE, Sum, Subtraction, Product, WeightedSum
from bms.blocks.nonlinear import CoulombVariableValue, Saturation, Coulomb

Cmax = 1000  # Max clutch torque handling
I1 = 0.5
I2 = 0.25
fv1 = 0.01
fv2 = 0.01
# e=bmsp.Step(1.,'e')

cc = Sinus(('Clutch command', 'cc'), 0.5, 0.1, 0, 0.5)
it = Step(('Input torque', 'it'), 200)
rt = Step(('Resistant torque', 'rt'), -180)

tc = bms.Variable(('Clutch Torque capacity', 'Tc'))
ct = bms.Variable(('clutch torque', 'ct'))
w1 = bms.Variable(('Rotational speed shaft 1', 'w1'))
w2 = bms.Variable(('Rotational speed shaft 2', 'w2'))
dw12 = bms.Variable(('Clutch differential speed', 'dw12'))
st1 = bms.Variable(('Sum torques on 1', 'st1'))
st2 = bms.Variable(('Sum torques on 2', 'st2'))


b1 = Gain(cc, tc, Cmax)
b2 = WeightedSum([w1, w2], dw12, [1, -1])
b3 = CoulombVariableValue(it, dw12, tc, ct, 1)
# b3=Coulomb(it,dw12,ct,150)

b4 = ODE(st1, w1, [1], [fv1, I1])
b5 = ODE(st2, w2, [1], [fv2, I2])
b6 = WeightedSum([it, ct], st1, [1, 1])
b7 = WeightedSum([rt, ct], st2, [1, -1])

ds = bms.DynamicSystem(50, 150, [b1, b2, b3, b4, b5, b6, b7])


# ds.DrawModel()
r = ds.Simulate()
ds.PlotVariables([[dw12, w1, w2], [tc, ct, rt, it]])
# ds.PlotVariables([[cc]])
