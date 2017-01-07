#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 16:10:58 2017

@author: steven
"""


import bms
from bms.physical.mechanical import ThermalEngine,Wheel,RotationalNode,TranslationalNode,Brake
from bms.blocks.continuous import WeightedSum
from bms.blocks.nonlinear import Saturation
from bms.signals.wltp import WLTP1

Vt=WLTP1('Target speed WLTP1')# Targeted Speed
SCx=0.29*2
mass=1200
r=0.22
wmin=1000*3.14/30
wmax=6000*3.14/30
Tmax=lambda w:300
fuel_flow=lambda w,c:w*c
I=3e-5
friction_v=0.009*mass
friction_c=0.01
Ge=1.5# Gain of engine throttle
Gb=1.6# Gain of brake
Tmax_b=1000 # Max braking torque
Vb=0.6# Speed error at beginning of braking

crankshaft=RotationalNode(I,friction_c,'crankshaft')
vehicle=TranslationalNode(mass,SCx,friction_v,'vehicle')

engine=ThermalEngine(crankshaft,wmin,wmax,Tmax,fuel_flow)
brake=Brake(crankshaft,Tmax_b)
wheels=Wheel(crankshaft,vehicle,r)

# Commands
subs1=WeightedSum([Vt,vehicle.variable],engine.commands[0],[Ge,-Ge])
v1=bms.Variable('',hidden=True)
subs2=WeightedSum([Vt,vehicle.variable],v1,[-Gb,Gb],-Vb)
sat1=Saturation(v1,brake.commands[0],0,1)


ps=bms.PhysicalSystem(600,600,[engine,wheels,brake],[subs1,subs2,sat1])
ds=ps.dynamic_system

#ds._ResolutionOrder2()
ds.Simulate()
ds.PlotVariables([[Vt,vehicle.variable],[engine.throttle,brake.commands[0]],[engine.max_torque,engine.variables[0]]])
