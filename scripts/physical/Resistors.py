# -*- coding: utf-8 -*-
"""
Serial resistors circuit with physical modelling
                    _______
           ___1_____|  R1  |______ 2
       +  _|_       |______|    __|__
       - |_G_|                  |   | R2 
           |                    |___|
           |______________________| 
                              3
"""

import bms
from bms.physical.electrical import Generator, Resistor, ElectricalNode, Capacitor, Ground
from bms.signals.functions import Sinus

U = Sinus('Generator', 4, 5)  # Voltage of generator
R1 = 200  # Resistance in Ohm
R2 = 200  # Resistance in Ohm

n1 = ElectricalNode('1')
n2 = ElectricalNode('2')
n3 = ElectricalNode('3')

gen = Generator(n3, n1, U)
res1 = Resistor(n1, n2, R1)
res2 = Resistor(n2, n3, R2)
gnd = Ground(n3)

ps = bms.PhysicalSystem(4, 300, [gen, res1, res2, gnd], [])
ds = ps.dynamic_system

# ds._ResolutionOrder2()
ds.Simulate()
ds.PlotVariables([[U, n1.variable, n2.variable, n3.variable],
                  [res1.variables[0], res2.variables[0]]])
