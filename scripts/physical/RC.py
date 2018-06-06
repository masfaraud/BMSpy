# -*- coding: utf-8 -*-
"""
RC circuit with physical modelling
                    _______
           ___1_____|  R   |______ 2
        +_|_        |______|    __|__
        |_G_|                   __ __ C 
        - |_________ _____________| 
                              3
"""

import bms
from bms.physical.electrical import Generator, Resistor, ElectricalNode, Capacitor, Ground
from bms.signals.functions import Sinus

U = Sinus('Generator', 2, 5)  # Voltage of generator
R = 10  # Resistance in Ohm
C = 0.01  # Capacitance in Fahrads

n1 = ElectricalNode('1')
n2 = ElectricalNode('2')
n3 = ElectricalNode('3')

gen = Generator(n3, n1, U)
res = Resistor(n1, n2, R)
cap = Capacitor(n2, n3, C)
gnd = Ground(n3)

ps = bms.PhysicalSystem(4, 300, [gen, res, cap, gnd], [])
ds = ps.dynamic_system

# ds._ResolutionOrder3()
d = ds.Simulate()
ds.PlotVariables([[U, n1.variable, n2.variable, n3.variable],
                  [res.variables[0], cap.variables[0]]])

# Validation: analytical solutions
