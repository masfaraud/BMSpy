# -*- coding: utf-8 -*-
"""

"""

from bms import PhysicalNode,PhysicalBlock,Variable,np
from bms.blocks.continuous import Sum,Gain,Subtraction,ODE
from bms.signals.functions import Step

class ElectricalNode(PhysicalNode):
    def __init__(self,name=''):
        PhysicalNode.__init__(self,name,'Voltage','Intensity')
        
class Resistor(PhysicalBlock):
    def __init__(self,node1,node2,R,name='Resistor'):
        PhysicalBlock.__init__(self,[node1,node2],name)
        self.R=R
        self.occurence_matrix=np.array([[1,1,1,0],[0,1,0,1]])#1st eq: (U1-U2)=R(i1-i2) 2nd: i1=i2
        
    def PartialDynamicSystem(self,ieq,variable):
        """
        returns dynamical system blocks associated to output variable
        """
#        print(ieq,variable.name)
        if ieq==0:
            # U1-U2=R(i1)
            if variable==self.nodes[0].variable:
                # U1 is output
                # U1=R(i1)+U2
                Ur=Variable(hidden=True)
                block1=Gain(self.variables[0],Ur,self.R)
                sum1=Sum([self.nodes[1].variable,Ur],variable)
                return [block1,sum1]
            elif variable==self.nodes[1].variable:
                # U2 is output
                # U2=-R(i1)+U2
                Ur=Variable(hidden=True)
                block1=Gain(self.variables[0],Ur,-self.R)
                sum1=Sum([self.nodes[0].variable,Ur],variable)
                return [block1,sum1]
            elif variable==self.variables[0]:
                # i1 is output
                # i1=(U1-U2)/R
                ir=Variable(hidden=True)
                subs1=Subtraction(self.nodes[0].variable,self.nodes[1].variable,ir)
                block1=Gain(ir,variable,1/self.R)
                return [block1,subs1]
        elif ieq==1:
            # i1=-i2
            if variable==self.variables[0]:
                #i1 as output
                return [Gain(self.variables[1],self.variables[0],-1)]
            elif variable==self.variables[1]:
                #i2 as output
                return [Gain(self.variables[0],self.variables[1],-1)]
            
                

#class Generator(PhysicalBlock):
#    def __init__(self,node1,node2,U):
#        PhysicalBlock.__init__(self,[node1,node2])
#        self.U=U
#        self.occurence_matrix=np.array([[1,0,1,0]])
        
      
class GeneratorGround(PhysicalBlock):
    """
    :param voltage_signal: BMS signal to be input function of voltage (Step,Sinus...)
    """
    def __init__(self,node1,node2,voltage_signal):
        PhysicalBlock.__init__(self,[node1,node2],'GeneratorGround')
        self.occurence_matrix=np.array([[1,0,0,0],[0,0,1,0]]) # 1st eq: U2=signal, U1=0 
        self.voltage_signal=voltage_signal

    def PartialDynamicSystem(self,ieq,variable):
        """
        returns dynamical system blocks associated to output variable
        """
        if ieq==0:
            # U1=0
            # U1 is output
            # U1=0
            zero=Step('Ground',0)
            equal=Gain(zero,variable,1)
            return [equal]
        elif ieq==1:
            # U1 is output
            # U1=0
            equal=Gain(self.voltage_signal,variable,1)
            return [equal]


class Capacitor(PhysicalBlock):
    def __init__(self,node1,node2,C):
        PhysicalBlock.__init__(self,[node1,node2],'Capacitor')
        self.C=C
        self.occurence_matrix=np.array([[1,1,1,0],[0,1,0,1]])#1st eq: (U1-U2)=R(i1-i2) 2nd: i1=i2
        
    def PartialDynamicSystem(self,ieq,variable):
        """
        returns dynamical system blocks associated to output variable
        """

        if ieq==0:
            # U1-U2=R(i1)
            if variable==self.nodes[0].variable:
                # U1 is output
                # U1=U2-
                Uc=Variable(hidden=True)
                block1=ODE(self.variables[0],Uc,[1],[0,self.C])
                sub1=Subtraction(self.nodes[1].variable,Uc,variable)
                return [block1,sub1]
            elif variable==self.nodes[1].variable:
                # U2 is output
                # U2=-R(i1)+U
                Uc=Variable(hidden=True)
                block1=ODE(self.variables[0],Uc,[1],[0,self.C])
                sum1=Sum([self.nodes[0].variable,Uc],variable)
                return [block1,sum1]
            elif variable==self.variables[0]:
                # i1 is output
                # i1=(U1-U2)/R
                ic=Variable(hidden=True)
                subs1=Subtraction(self.nodes[0].variable,self.nodes[1].variable,ic)
                block1=ODE(ic,variable,[0,self.C],[1])
                return [block1,subs1]
        elif ieq==1:
            # i1=-i2
            if variable==self.variables[0]:
                #i1 as output
                return [Gain(self.variables[1],self.variables[0],-1)]
            elif variable==self.variables[1]:
                #i2 as output
                return [Gain(self.variables[0],self.variables[1],-1)]
