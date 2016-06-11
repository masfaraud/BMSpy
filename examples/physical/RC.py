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
from bms.physical.electrical import GeneratorGround,Resistor,ElectricalNode

U=12# Voltage of generator
R=10# Resistance in Ohm
C=0.01# Capacitance in 

n1=ElectricalNode('1')
n2=ElectricalNode('2')
#n3=ElectricalNode('3')

Gen=GeneratorGround(n2,n1,U)
Res=Resistor(n1,n2,R)

ps=bms.PhysicalSystem([n1,n2],[Gen,Res])
ps.GenerateDynamicSystem()