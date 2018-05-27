# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 22:11:00 2015

@author: steven
"""

import bms
from bms.signals.functions import Step
from bms.blocks.continuous import Gain, ODE, Sum, Subtraction, Product
from bms.blocks.nonlinear import Coulomb, Saturation

R = 0.3
L = 0.2
J = 0.2
k = 0.17
Tr = 3  # Torque requested on motor output
Gc = 8  # Gain corrector
tau_i = 3
Umax = 48  # Max voltage motor
# Imax=10# Max intensity motor


# e=bmsp.Step(1.,'e')

Wc = Step(('Rotationnal speed command', 'wc'), 100.)

dW = bms.Variable(('delta rotationnal speed', 'dW'))
Up = bms.Variable(('Voltage corrector proportionnal', 'Ucp'))
Ui = bms.Variable(('Voltage corrector integrator', 'Uci'))
Uc = bms.Variable(('Voltage command', 'Uc'))
Um = bms.Variable(('Voltage Input motor', 'Uim'))
e = bms.Variable(('Counter electromotive force', 'Cef'))
Uind = bms.Variable(('Voltage Inductor', 'Vi'))
Iind = bms.Variable(('Intensity Inductor', 'Ii'))
Tm = bms.Variable(('Motor torque', 'Tm'))
Text = bms.Variable(('Resistant torque', 'Tr'))
T = bms.Variable(('Torque', 'T'))
W = bms.Variable(('Rotationnal speed', 'w'))
Pe = bms.Variable(('Electrical power', 'Pe'))
Pm = bms.Variable(('Mechanical power', 'Pm'))


block1 = Subtraction(Wc, W, dW)
block2 = ODE(dW, Ui, [1], [0, tau_i])
block3 = Gain(dW, Up, Gc)
block4 = Sum([Up, Ui], Uc)
block4a = Saturation(Uc, Um, -Umax, Umax)
block5 = Subtraction(Um, e, Uind)
block6 = ODE(Uind, Iind, [1], [R, L])
block7 = Gain(Iind, Tm, k)
block8 = Sum([Tm, Text], T)
block8a = Coulomb(Tm, W, Text, Tr, 2)
block9 = ODE(T, W, [1], [0, J])
block10 = Gain(W, e, k)
block11 = Product(Um, Iind, Pe)
block11a = Product(Tm, W, Pm)
ds = bms.DynamicSystem(10, 1000, [block1, block2, block3, block4, block4a,
                                  block5, block6, block7, block8, block8a, block9, block10, block11, block11a])


# ds.DrawModel()
r = ds.Simulate()
# r=ds._ResolutionOrder()
# print(ba)
ds.PlotVariables([[Wc, W, dW], [Tm, Text, T], ])
ds.PlotVariables([[Um, e, Uind], [Pe, Pm], [Iind]])
