# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 22:11:00 2015

@author: steven
"""

import sys
sys.path.append('../')
import bms

R=1.
L=0.001
J=10
k=100

#e=bmsp.Step(1.,'e')
Ui=bms.Step(1.,'Input Voltage')
e=bms.Variable([0],'e')
U1=bms.Variable([0],'U1')
i=bms.Variable([0],'i')

s=bms.Variable([0],'s')

block1=bms.SumBlock(Ui,e,U1)
block2=bms.ODEBlock(U1,i,[1],[R,L])
block3=bms.ODEBlock(i,e,[k],[1])
ds=bms.DynamicSystem(10,100,[block1,block2,block3])
#res=ds.ResolutionOrder()
#print(res)
ds.Simulate()