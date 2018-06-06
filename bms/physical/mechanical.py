# -*- coding: utf-8 -*-
"""

"""

from bms import PhysicalNode, PhysicalBlock, Variable, np
from bms.blocks.continuous import Gain, ODE, WeightedSum, Product, FunctionBlock
from bms.blocks.nonlinear import Saturation, Sign
#from bms.signals.functions import Step


class RotationalNode(PhysicalNode):
    def __init__(self, inertia, friction, name=''):
        PhysicalNode.__init__(self, True, True, name,
                              'Rotational speed', 'Torque')
        self.inertia = inertia
        self.friction = friction

    def ConservativeLaw(self, flux_variables, output_variable):
        if output_variable == self.variable:
            v1 = Variable(hidden='True')
            b1 = WeightedSum(flux_variables, v1, [
                             1]*len(flux_variables), -self.friction)
            b2 = ODE(v1, self.variable, [1], [0, self.inertia])
            return[b1, b2]
        else:
            v1 = Variable(hidden='True')
            b1 = ODE(self.variable, v1, [0, self.inertia], [1])
            b2 = WeightedSum([v1]+flux_variables, output_variable,
                             [1]+[-1]*len(flux_variables), self.friction)
            return[b1, b2]


class TranslationalNode(PhysicalNode):
    def __init__(self, mass, SCx, friction, name=''):
        PhysicalNode.__init__(self, True, True, name, 'Speed', 'Force')
        self.mass = mass
        self.SCx = SCx
        self.friction = friction

    def ConservativeLaw(self, flux_variables, output_variable):
        if output_variable == self.variable:
            v1 = Variable(hidden='True')
            b1 = WeightedSum(flux_variables, v1, [
                             1]*len(flux_variables), -self.friction)
            b2 = ODE(v1, self.variable, [1], [self.SCx, self.mass])
            return[b1, b2]
        else:
            v1 = Variable(hidden='True')
            b1 = ODE(self.variable, v1, [self.SCx, self.mass], [1])
            b2 = WeightedSum([v1]+flux_variables, output_variable,
                             [1]+[-1]*len(flux_variables), self.friction)
            return[b1, b2]


class ThermalEngine(PhysicalBlock):
    """
    Simple thermal engine
    """

    def __init__(self, node1, wmin, wmax, Tmax_map, fuel_flow_map, name='Thermal engine'):
        occurence_matrix = np.array([[0, 1]])
        command = Variable('Requested engine throttle')
        self.wmin = wmin
        self.wmax = wmax
        self.Tmax = Tmax_map
        self.fuel_flow_map = fuel_flow_map
        self.max_torque = Variable('max torque')
        self.throttle = Variable('Engine throttle')

        PhysicalBlock.__init__(
            self, [node1], [0], occurence_matrix, [command], name)

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """
        if ieq == 0:
            # U1=0
            if variable == self.variables[0]:
                b1 = FunctionBlock(
                    self.physical_nodes[0].variable, self.max_torque, self.Tmax)
                b2 = Saturation(self.commands[0], self.throttle, 0, 1)
                b3 = Product(self.max_torque, self.throttle, variable)
                return[b1, b2, b3]


class Brake(PhysicalBlock):
    """
    Simple brake, must be improved with non linearity of equilibrium
    """

    def __init__(self, node1, Tmax, name='Brake'):
        occurence_matrix = np.array([[0, 1]])
        command = Variable('Brake command')
        self.Tmax = Tmax
        PhysicalBlock.__init__(
            self, [node1], [0], occurence_matrix, [command], name)

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """
        if ieq == 0:
            # U1=0
            if variable == self.variables[0]:
                return[Gain(self.commands[0], variable, -self.Tmax)]


class Clutch(PhysicalBlock):
    """
    Simple clutch
    """

    def __init__(self, node1, node2, Tmax, name='Clutch'):
        occurence_matrix = np.array([[0, 1, 0, 0], [0, 1, 0, 1]])
        command = Variable('Clutch command')
        self.Tmax = Tmax
        PhysicalBlock.__init__(self, [node1, node2], [
                               0, 1], occurence_matrix, [command], name)

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """
        if ieq == 0:
            # C1=-f*Tmax*sign(w1-w2)
            if variable == self.variables[0]:
                ut = Variable('unsigned clutch friction torque', hidden=True)
                b1 = Gain(self.commands[0], ut, self.Tmax)
                dw = Variable('Delta rotationnal speed', hidden=True)
                sdw = Variable('Sign of delta rotationnal speed')
                b2 = WeightedSum(
                    [self.physical_nodes[0].variable, self.physical_nodes[1].variable], dw, [-1, 1])
                b3 = Sign(dw, sdw)
                b4 = Product(ut, sdw, variable)
                return[b1, b2, b3, b4]
        elif ieq == 1:
            # C1=-C2
            if variable == self.variables[0]:
                return [Gain(self.variables[1], variable, -1)]
            if variable == self.variables[1]:
                return [Gain(self.variables[0], variable, -1)]


class GearRatio(PhysicalBlock):
    """
        Allow to model all components that impose a fixed ratio between two
        rotational nodes such as gear sets
    """

    def __init__(self, node1, node2, ratio, name='Gear ratio'):
        occurence_matrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1]])
        self.ratio = ratio
        PhysicalBlock.__init__(self, [node1, node2], [
                               0, 1], occurence_matrix, [], name)

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """
        if ieq == 0:
            # w2=Rw1
            if variable == self.physical_nodes[0].variable:
                # w1=w2/R
                return[Gain(self.physical_nodes[1].variable, variable, 1/self.ratio)]
            elif variable == self.physical_nodes[1].variable:
                # w2=Rw1
                return[Gain(self.physical_nodes[0].variable, variable, self.ratio)]
        elif ieq == 1:
            # C1=-RC2
            if variable == self.variables[0]:
                # C1=-RC2
                return[Gain(self.variables[1], variable, -self.ratio)]
            elif variable == self.variables[1]:
                # C2=-C1/R
                return[Gain(self.variables[0], variable, -1/self.ratio)]


class Wheel(PhysicalBlock):
    """

    """

    def __init__(self, node_rotation, node_translation, wheels_radius, name='Wheel'):
        occurence_matrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1]])
        self.wheels_radius = wheels_radius
        PhysicalBlock.__init__(self, [node_rotation, node_translation], [
                               0, 1], occurence_matrix, [], name)

    def PartialDynamicSystem(self, ieq, variable):
        """
        returns dynamical system blocks associated to output variable
        """
        if ieq == 0:
            # v=Rw
            if variable == self.physical_nodes[0].variable:
                # W=V/r
                return[Gain(self.physical_nodes[1].variable, variable, 1/self.wheels_radius)]
            elif variable == self.physical_nodes[1].variable:
                # V=rw
                return[Gain(self.physical_nodes[0].variable, variable, self.wheels_radius)]
        elif ieq == 1:
            # C=-FR
            if variable == self.variables[0]:
                # C=-FR
                return[Gain(self.variables[1], variable, -self.wheels_radius)]
            elif variable == self.variables[1]:
                # F=-C/R
                return[Gain(self.variables[0], variable, -1/self.wheels_radius)]
