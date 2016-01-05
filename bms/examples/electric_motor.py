# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 22:11:00 2015

@author: steven
"""

import bms

R=0.3
L=0.2
J=0.2
k=0.17
Tr=3# Torque requested on motor output
Gc=8# Gain corrector
tau_i=3
Umax=48# Max voltage motor
#Imax=10# Max intensity motor


#e=bmsp.Step(1.,'e')

Wc=bms.Step('Rotationnal speed command',100.)

dW=bms.Variable('delta rotationnal speed')
Up=bms.Variable('Voltage corrector proportionnal')#
Ui=bms.Variable('Voltage corrector integrator')#
Uc=bms.Variable('Voltage command')
Um=bms.Variable('Voltage Input motor')
e=bms.Variable('Counter electromotive force')
Uind=bms.Variable('Voltage Inductor')
Iind=bms.Variable('Intensity Inductor')
Tm=bms.Variable('Motor torque')
Text=bms.Variable('Resistant torque')
T=bms.Variable('Torque')
W=bms.Variable('Rotationnal speed')
Pe=bms.Variable('Electrical power')
Pm=bms.Variable('Mechanical power')

s=bms.Variable('s')

block1=bms.Subtraction(Wc,W,dW)
block2=bms.ODE(dW,Ui,[1],[0,tau_i])
block3=bms.Gain(dW,Up,Gc)
block4=bms.Sum(Up,Ui,Uc)
block4a=bms.Saturation(Uc,Um,-Umax,Umax)
block5=bms.Subtraction(Um,e,Uind)
block6=bms.ODE(Uind,Iind,[1],[R,L])
block7=bms.Gain(Iind,Tm,k)
block8=bms.Sum(Tm,Text,T)
block8a=bms.Coulomb(Tm,W,Text,Tr,2)
block9=bms.ODE(T,W,[1],[0,J])
block10=bms.Gain(W,e,k)
block11=bms.Product(Um,Iind,Pe)
block11a=bms.Product(Tm,W,Pm)
ds=bms.DynamicSystem(10,2000,[block1,block2,block3,block4,block4a,block5,block6,block7,block8,block8a,block9,block10,block11,block11a])


#ds.DrawModel()
ds.Simulate()
ds.PlotVariables([[Wc,W,dW],[Tm,Text,T],])
ds.PlotVariables([[Um,e,Uind],[Pe,Pm],[Iind]])

