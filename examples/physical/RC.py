# -*- coding: utf-8 -*-
"""
RC circuit with physical modelling
                    _______
           ___1_____|  R   |______ 2
       +___|___     |______|    __|__
       -  ___                   __ __ C 
           |______________________| 
                              3
"""

import bms
from bms.physical.electrical import GeneratorGround,Resistor,ElectricalNode,Capacitor
from bms.signals.functions import Sinus

U=Sinus('Generator',2,5)# Voltage of generator
R=100# Resistance in Ohm
C=0.01# Capacitance in Fahrads

n1=ElectricalNode('1')
n2=ElectricalNode('2')
n3=ElectricalNode('3')

Gen=GeneratorGround(n3,n1,U)
Res=Resistor(n1,n2,R)
Cap=Capacitor(n2,n3,C)

ps=bms.PhysicalSystem(4,100,[n1,n2],[Gen,Res,Cap])
ds=ps.GenerateDynamicSystem()

ds.Simulate()
ds.PlotVariables([[U,n1.variable,n2.variable,n3.variable],[Res.variables[0],Cap.variables[0]]])