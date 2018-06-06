#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 16:10:58 2017

@author: steven
"""


import bms
from bms.physical.mechanical import ThermalEngine, Wheel, RotationalNode, TranslationalNode, Brake, Clutch, GearRatio
from bms.blocks.continuous import WeightedSum, Gain
from bms.blocks.nonlinear import Saturation
from bms.signals.wltp import WLTP1
#from bms.signals.functions import Step

Vt = WLTP1('Target speed WLTP1')  # Targeted Speed
SCx = 0.29*2
mass = 1200
r = 0.22
wmin = 900*3.14/30
wmax = 6000*3.14/30


def Tmax(w): return 160


def fuel_flow(w, c): return w*c


Ic = 3.5
Igb1 = 1.2
Igb2 = 0.5e-1

friction_v = 0.009*mass

friction_c = 0.01
Ge = 1.5  # Gain of engine throttle
Gb = 1.1  # Gain of brake
Tmax_b = 10000  # Max braking torque
Tmax_c = 140  # Max clutch friction torque

wec = 900*3.14/30  # Engaging clutch rotational speed
wrc = 1200*3.14/30  # Releasing clutch rotational speed

Vb = 0.3  # Speed error at beginning of braking
r1 = 0.05

crankshaft = RotationalNode(Ic, friction_c, 'crankshaft')
shaft_gb1 = RotationalNode(Igb1, friction_c, 'shaft gb1')
shaft_gb2 = RotationalNode(Igb2, friction_c, 'shaft gb2')
vehicle = TranslationalNode(mass, SCx, friction_v, 'vehicle')

engine = ThermalEngine(crankshaft, wmin, wmax, Tmax, fuel_flow)
clutch = Clutch(crankshaft, shaft_gb1, Tmax_c)
gr1 = GearRatio(shaft_gb1, shaft_gb2, 0.05)
brake = Brake(shaft_gb2, Tmax_b)
wheels = Wheel(shaft_gb2, vehicle, r)

# Commands
subs1 = WeightedSum([Vt, vehicle.variable], engine.commands[0], [Ge, -Ge])
v1 = bms.Variable('', hidden=True)
subs2 = WeightedSum([Vt, vehicle.variable], v1, [-Gb, Gb], -Vb)
sat1 = Saturation(v1, brake.commands[0], 0, 1)

# clutch
cc = bms.Variable('Clutch command')
gc = Gain(crankshaft.variable, cc, 1/(wrc-wec), wec/(wec-wrc))
satc = Saturation(cc, clutch.commands[0], 0, 1)

ps = bms.PhysicalSystem(600, 600, [engine, gr1, clutch, wheels, brake], [
                        subs1, subs2, sat1, gc, satc])
ds = ps.dynamic_system

# ds._ResolutionOrder2()
ds.Simulate()
ds.PlotVariables([[Vt, vehicle.variable], [engine.throttle, brake.commands[0],
                                           clutch.commands[0]], [engine.max_torque, engine.variables[0]]])
ds.PlotVariables(
    [[crankshaft.variable, shaft_gb1.variable, shaft_gb2.variable]])
ds.PlotVariables([[wheels.variables[0], clutch.variables[0]]])
