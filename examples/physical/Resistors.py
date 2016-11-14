# -*- coding: utf-8 -*-
"""
Serial resistors circuit with physical modelling
                    _______
           ___1_____|  R1  |______ 2
       +___|___     |______|    __|__
       -  ___                   |   | R2 
           |                    |___|
           |______________________| 
                              3
"""

import bms
from bms.physical.electrical import GeneratorGround,Resistor,ElectricalNode,Capacitor
from bms.signals.functions import Sinus

U=Sinus('Generator',4,5)# Voltage of generator
R1=200# Resistance in Ohm
R2=400# Resistance in Ohm

n1=ElectricalNode('1')
n2=ElectricalNode('2')
n3=ElectricalNode('3')

Gen=GeneratorGround(n3,n1,U)
Res1=Resistor(n1,n2,R1)
Res2=Resistor(n2,n3,R2)

ps=bms.PhysicalSystem(4,300,[Gen,Res1,Res2])
ds=ps.dynamic_system

#ds._ResolutionOrder2()
ds.Simulate()
ds.PlotVariables([[U,n1.variable,n2.variable,n3.variable],[Res1.variables[0],Res2.variables[0]]])

# Validation: analytical solutions

# Debug
#ro=ds._ResolutionOrder()
#for b in ro:
#    print(b)
#    print('inputs')
#    for var in b.inputs:
#        print(var.name)
#    print('outputs')
#    for var in b.outputs:
#        print(var.name)
