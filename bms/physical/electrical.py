# -*- coding: utf-8 -*-
"""

"""

from bms import PhysicalNode, PhysicalBlock, Variable, np
from bms.blocks.continuous import Sum, Gain, Subtraction, ODE, WeightedSum, Product
from bms.blocks.nonlinear import Saturation
from bms.signals.functions import Step


class ElectricalNode(PhysicalNode):
    def __init__(self, name=''):
        PhysicalNode.__init__(self, False, True, name, 'Voltage', 'Intensity')

    def ConservativeLaw(self, flux_variables, output_variable):
        return [WeightedSum(flux_variables, output_variable, [-1]*len(flux_variables))]


class Ground(PhysicalBlock):
    def __init__(self, node1, name='Ground'):
        occurence_matrix = np.array([[1, 0]])  # U1=0
        PhysicalBlock.__init__(self, [node1], [], occurence_matrix, [], name)

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """
        if ieq == 0:
            # U1=0
            if variable == self.physical_nodes[0].variable:
                v = Step('Ground', 0)
                return[Gain(v, variable, 1)]


class Resistor(PhysicalBlock):
    def __init__(self, node1, node2, R, name='Resistor'):
        # 1st eq: (U1-U2)=R(i1-i2) 2nd: i1=-i2
        occurence_matrix = np.array([[1, 1, 1, 0], [0, 1, 0, 1]])
        PhysicalBlock.__init__(self, [node1, node2], [
                               0, 1], occurence_matrix, [], name)
        self.R = R

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """
#        print(ieq,variable.name)
        if ieq == 0:
            # U1-U2=R(i1)
            if variable == self.physical_nodes[0].variable:
                # U1 is output
                # U1=R(i1)+U2
                return [WeightedSum([self.physical_nodes[1].variable, self.variables[0]], variable, [1, self.R])]
            elif variable == self.physical_nodes[1].variable:
                # U2 is output
                # U2=-R(i1)+U2
                return [WeightedSum([self.physical_nodes[0].variable, self.variables[0]], variable, [1, -self.R])]
            elif variable == self.variables[0]:
                # i1 is output
                # i1=(U1-U2)/R
                return [WeightedSum([self.physical_nodes[0].variable, self.physical_nodes[1].variable], variable, [1/self.R, -1/self.R])]
        elif ieq == 1:
            # i1=-i2
            if variable == self.variables[0]:
                # i1 as output
                return [Gain(self.variables[1], self.variables[0], -1)]
            elif variable == self.variables[1]:
                # i2 as output
                return [Gain(self.variables[0], self.variables[1], -1)]


class Generator(PhysicalBlock):
    """
    :param voltage_signal: BMS signal to be input function of voltage (Step,Sinus...)
    """

    def __init__(self, node1, node2, voltage_signal, name='GeneratorGround'):
        occurence_matrix = np.array([[1, 0, 1, 0]])  # 1st eq: U2=signal, U1=0
        PhysicalBlock.__init__(self, [node1, node2], [
                               0, 1], occurence_matrix, [], name)
        self.voltage_signal = voltage_signal

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """
        if ieq == 0:
            # U2-U1=signal
            if variable == self.physical_nodes[0].variable:
                # U1 is output
                # U1=U2-signal
                return [WeightedSum([self.physical_nodes[1].variable, self.voltage_signal], variable, [1, -1])]
            elif variable == self.physical_nodes[1].variable:
                # U2 is output
                # U2=U1+signal
                return [WeightedSum([self.physical_nodes[0].variable, self.voltage_signal], variable, [1, 1])]


# class Battery(PhysicalBlock):
#    """
#    Caution: still a bug, soc=0 doesn't imply i=0
#    : param Umax: Voltage when soc=1
#    : param Umin: Voltage when soc=0
#    : param C: capacity of battery in W.s
#
#    """
#    def __init__(self,node1,node2,Umin,Umax,C,initial_soc,R,name='Battery'):
# occurence_matrix=np.array([[1,1,1,0],[0,1,0,1]]) # 1st eq: U2=signal, U1=0
#        occurence_matrix=np.array([[1,1,1,0]]) # 1st eq: U2=signal, U1=0
#        PhysicalBlock.__init__(self,[node1,node2],[0,1],occurence_matrix,[],name)
#        self.Umax=Umax
#        self.Umin=Umin
#        self.C=C
#        self.R=R
#        self.initial_soc=initial_soc
#        self.soc=Variable('Battery SoC',[initial_soc])
#        self.U=Variable('Battery voltage')
#
#    def PartialDynamicSystem(self,ieq,variable):
#        """
#        returns dynamical system blocks associated to output variable
#        """
#        if ieq==0:
#            # Soc determination
#            # soc=1-UI/CP
#            v1=Variable('UI',hidden=True)#UI
#            v2=Variable('UI/CP',hidden=True)#UI/CP
#            v3=Variable('soc0-UI/CP',hidden=True)#soc0-UI/CP
#            b1=Product(self.U,self.variables[0],v1)
#            b2=ODE(v1,v2,[1],[1,self.C])
#            b3=WeightedSum([v2],v3,[-1],self.initial_soc)
#            b4=Saturation(v3,self.soc,0,1)
#            b5=WeightedSum([self.soc],self.U,[self.Umax-self.Umin],self.Umin)
#            blocks=[b1,b2,b3,b4,b5]
#            # U2-U1=U+Ri1
#            # U=soc(Umax-Umin)+Umin
#            if variable==self.physical_nodes[0].variable:
#                print('Bat0#1')
#                # U1 is output
#                # U1=-U-Ri1+U2
#                blocks.append(WeightedSum([self.U,self.variables[0],self.physical_nodes[1].variable],variable,[-1,-self.R,1]))
#            elif variable==self.physical_nodes[1].variable:
#                print('Bat0#2')
#                # U2 is output
#                # U2=U1+Ri1+U
#                blocks.append(WeightedSum([self.physical_nodes[0].variable,self.variables[0],self.U],variable,[1,self.R,1]))
#
#            elif variable==self.variables[0]:
#                print('Bat0#3')
#                # i1 is output
#                # i1=(-U1+U2-U)/R
#                blocks.append(WeightedSum([self.physical_nodes[0].variable,self.physical_nodes[1].variable,self.U],variable,[-1/self.R,1/self.R,-1/self.R]))
#
#            return blocks


class Capacitor(PhysicalBlock):
    def __init__(self, node1, node2, C, name='Capacitor'):
        # 1st eq: (U1-U2)=R(i1-i2) 2nd: i1=-i2
        occurence_matrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1]])
        PhysicalBlock.__init__(self, [node1, node2], [
                               0, 1], occurence_matrix, [], name)
        self.C = C

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """

        if ieq == 0:

            if variable == self.physical_nodes[0].variable:
                print('1')
                # U1 is output
                # U1=i1/pC+U2
                Uc = Variable(hidden=True)
                block1 = ODE(self.variables[0], Uc, [1], [0, self.C])
                sub1 = Sum([self.physical_nodes[1].variable, Uc], variable)
                return [block1, sub1]
            elif variable == self.physical_nodes[1].variable:
                print('2')
                # U2 is output
                # U2=U1-i1/pC
                Uc = Variable(hidden=True)
                block1 = ODE(self.variables[0], Uc, [-1], [0, self.C])
                sum1 = Sum([self.physical_nodes[0].variable, Uc], variable)
                return [block1, sum1]
#            elif variable==self.variables[0]:
#                print('3')
#                # i1 is output
#                # i1=pC(U1-U2)
#                ic=Variable(hidden=True)
#                subs1=Subtraction(self.physical_nodes[0].variable,self.physical_nodes[1].variable,ic)
#                block1=ODE(ic,variable,[0,self.C],[1])
#                return [block1,subs1]
        elif ieq == 1:
            # i1=-i2
            if variable == self.variables[0]:
                # i1 as output
                #                print('Bat1#0')
                return [Gain(self.variables[1], self.variables[0], -1)]
            elif variable == self.variables[1]:
                # i2 as output
                #                print('Bat1#1')
                return [Gain(self.variables[0], self.variables[1], -1)]


class Inductor(PhysicalBlock):
    def __init__(self, node1, node2, L, name='Inductor'):
        # 1st eq: (U1-U2)=Ldi1/dt 2nd: i1=-i2
        occurence_matrix = np.array([[1, 1, 1, 0], [0, 1, 0, 1]])
        PhysicalBlock.__init__(self, [node1, node2], [
                               0, 1], occurence_matrix, [], name)
        self.L = L

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """

        if ieq == 0:

            #            if variable==self.physical_nodes[0].variable:
            # print('1')
            #                # U1 is output
            #                # U1=i1/pC+U2
            #                Uc=Variable(hidden=True)
            #                block1=ODE(self.variables[0],Uc,[1],[0,self.C])
            #                sub1=Sum([self.physical_nodes[1].variable,Uc],variable)
            #                return [block1,sub1]
            #            elif variable==self.physical_nodes[1].variable:
            #                print('2')
            #                # U2 is output
            #                # U2=U1-i1/pC
            #                Uc=Variable(hidden=True)
            #                block1=ODE(self.variables[0],Uc,[-1],[0,self.C])
            #                sum1=Sum([self.physical_nodes[0].variable,Uc],variable)
            #                return [block1,sum1]
            if variable == self.variables[0]:  # i1=(u1-u2)/Lp
                print('3')
                # i1 is output
                # i1=pC(U1-U2)
                Uc = Variable(hidden=True)
                subs1 = Subtraction(
                    self.physical_nodes[0].variable, self.physical_nodes[1].variable, Uc)
                block1 = ODE(Uc, variable, [1], [0, self.L])
                return [block1, subs1]
        elif ieq == 1:
            # i1=-i2
            if variable == self.variables[0]:
                # i1 as output
                return [Gain(self.variables[1], self.variables[0], -1)]
            elif variable == self.variables[1]:
                # i2 as output
                return [Gain(self.variables[0], self.variables[1], -1)]
