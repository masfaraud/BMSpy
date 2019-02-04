# -*- coding: utf-8 -*-
"""Collection of non-linear blocks

"""

from bms import Block
import numpy as np


# class DeadZone(Block):
#    """
#
#    """
#    def __init__(self,input_variable,output_variable,zone_width):
#        Block.__init__(self,[input_variable,trigger_variable],[output_variable],1,0)
#        self.zone_width=zone_width
#
#    def Evaluate(self,it,ts):
#        input_value=self.InputValues(it)[0]
#        if value<-0.5*self.zone_width:
#            output=value+0.5*self.zone_width
#        elif value>-0.5*self.zone_width:
#            output=value-0.5*self.zone_width
#        else:
#            output=0
#        self.outputs[0]._values[it]=output


# class Hysteresis(Block):
#    """
#
#    """
#    def __init__(self,input_variable,output_variable,zone_width,initial_value):
#        Block.__init__(self,[input_variable,trigger_variable],[output_variable],1,0)
#        self.zone_width=zone_width
#        self.value=initial_value
#
#    def Evaluate(self,it,ts):
#        input_value=self.InputValues(it)[0]
#        if self.value>input_value+0.5*self.zone_width:
#            output=input_value+0.5*self.zone_width
#            self.value=output
#        elif self.value<input_value-0.5*self.zone_width:
#            output=input_value-0.5*self.zone_width
#            self.value=output
#        return output


class Delay(Block):
    """
    Simple block to delay output with respect to input.
    
    :param delay: a delay in seconds
    """
    def __init__(self, input_variable, output_variable, delay):
        Block.__init__(self, [input_variable], [output_variable], 1, 0)
        self.delay = delay
        if delay < 0:
            raise ValueError

    def Evaluate(self, it, ts):

        delay_in_steps = int(self.delay // ts)
        delay_remainder = self.delay % ts
        if (it - delay_in_steps -1) < 0:
#            print(it, 'a', self.inputs[0].initial_values[-1])
            return self.inputs[0].initial_values[-1]
        else:
            # Performing interpolation
            v1 = self.inputs[0]._values[it - delay_in_steps-1]
            v2 = self.inputs[0]._values[it - delay_in_steps]
            return (ts-delay_remainder)/ts*(v2-v1) +v1 
            
    def Label(self):
        return 'delay'


class Saturation(Block):
    """Defines a saturation block.

    .. math::
        output = 
        \\begin{cases}
            min\_value, & \\textrm{if } input < min\_value

            max\_value, & \\textrm{if } input > max\_value

            input, & \\textrm{if } min\_value \leq input \leq max\_value
        \\end{cases}

    Args:
        input_variable (Variable): This is the input of the block.
        output_variable (Variable): This is the output of the block.
        min_value: This is the lower bound for the output.
        max_value: This is the upper bound for the output.
    """

    def __init__(self, input_variable, output_variable, min_value, max_value):
        Block.__init__(self, [input_variable], [output_variable], 1, 0)
        self.min_value = min_value
        self.max_value = max_value

    def Evaluate(self, it, ts):
        value = self.InputValues(it)[0]
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        return np.array([value])

    def LabelBlock(self):
        return 'Sat'


class Coulomb(Block):
    """
        Return coulomb force under condition of speed and sum of forces (input)

    """

    def __init__(self, input_variable, speed_variable, output_variable, max_value, tolerance=0):
        Block.__init__(self, [input_variable, speed_variable], [
                       output_variable], 1, 0)
        self.max_value = max_value
        self.tolerance = tolerance

    def Evaluate(self, it, ts):
        input_value, speed = self.InputValues(it)
        if speed > self.tolerance:
            output = -self.max_value
        elif speed < -self.tolerance:
            output = self.max_value
        else:
            if abs(input_value) < self.max_value:
                output = -input_value
            else:
                if input_value < 0:
                    output = self.max_value
                else:
                    output = -self.max_value

        return np.array([output])

    def LabelBlock(self):
        return 'Clb'


class CoulombVariableValue(Block):
    """
        Return coulomb force under condition of speed and sum of forces (input)
        The max value is driven by an input
    """

    def __init__(self, external_force, speed_variable, value_variable, output_variable, tolerance=0):
        Block.__init__(self, [external_force, speed_variable, value_variable], [
                       output_variable], 1, 0)
#        self.max_value=max_value
        self.tolerance = tolerance

    def Evaluate(self, it, ts):
        external_force, speed, max_value = self.InputValues(it)
        # Slipping
        if speed > self.tolerance:
            output = -max_value
        elif speed < -self.tolerance:
            output = max_value
        else:
            # locked
            if abs(external_force) < max_value:
                # equilibrium
                output = -external_force
            else:
                # Breaking equilibrium
                if external_force < 0:
                    output = max_value
                else:
                    output = -max_value
        return output

    def LabelBlock(self):
        return 'Clb Var'


class RegCoulombVariableValue(Block):
    """
        Return coulomb force under condition of speed and sum of forces (input)
        The max value is driven by an input
    """

    def __init__(self, external_force, speed_variable, value_variable, output_variable, tolerance=0):
        Block.__init__(self, [external_force, speed_variable, value_variable], [
                       output_variable], 1, 0)
#        self.max_value=max_value
        self.tolerance = tolerance

    def Evaluate(self, it, ts):
        external_force, speed, max_value = self.InputValues(it)
        # Slipping
        if speed > self.tolerance:
            output = -max_value
        elif speed < -self.tolerance:
            output = max_value
        else:
            # locked
            if abs(external_force) < max_value:
                # equilibrium
                output = -external_force
            else:
                # Breaking equilibrium
                if external_force < 0:
                    output = max_value
                else:
                    output = -max_value
        return output

    def LabelBlock(self):
        return 'Clb Var'


class Sign(Block):
    """Defines a sign operation on the input.

    .. math::
        output = 
        \\begin{cases}
        -1, & \\textrm{if } input < 0

        0, & \\textrm{if } input = 0

        1, & \\textrm{if } input > 0
        \\end{cases}
        
    """

    def __init__(self, input_variable, output_variable):
        Block.__init__(self, [input_variable], [output_variable], 1, 0)

    def Evaluate(self, it, ts):
        input_value = self.InputValues(it)[0]
        if input_value < 0:
            output = -1
        elif input_value > 0:
            output = 1
        else:
            output = 0
#        print(input_value,speed,output)
        return np.array([output])

    def LabelBlock(self):
        return 'Sgn'
