# -*- coding: utf-8 -*-
"""
RLC circuit with physical modelling
                    _______
           ___1_____|  R   |______ 2
        +_|_        |______|      |
        |   |                     /
        | G |                  L  \
        |___|          C          /
        - |___________| |_________| 
          4           | |         3
"""

import bms
from bms.physical.electrical import Generator, Resistor, ElectricalNode, Capacitor, Ground, Inductor
from bms.signals.functions import Sinus

U = Sinus('Generator', 2, 5)  # Voltage of generator
R = 10  # Resistance in Ohm
C = 0.01  # Capacitance in Fahrads
L = 0.025  # Inductance in Henry

n1 = ElectricalNode('1')
n2 = ElectricalNode('2')
n3 = ElectricalNode('3')
n4 = ElectricalNode('4')

gen = Generator(n4, n1, U)
res = Resistor(n1, n2, R)
cap = Capacitor(n2, n3, C)
ind = Inductor(n3, n4, L)
gnd = Ground(n4)

ps = bms.PhysicalSystem(4, 300, [gen, res, cap, gnd, ind], [])
ds = ps.dynamic_system

# ds._ResolutionOrder3()
d = ds.Simulate()
ds.PlotVariables([[U, n1.variable, n2.variable, n3.variable],
                  [res.variables[0], cap.variables[0]]])

# Validation: analytical solutions
