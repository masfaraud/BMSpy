# -*- coding: utf-8 -*-
"""Collection of continuous blocks

"""

from bms import Block
import numpy as np
from scipy.special import factorial


class Gain(Block):
    """Defines a gain operation.

    .. math:: output = (value \\times input) + offset

    Args:
        input_variable (Variable): This is the input of the block.
        output_variable (Variable): This is the output of the block.
        gain: This is what multiplies the input.
        offset: This is added to the input after being multiplied.

    """

    def __init__(self, input_variable, output_variable, value, offset=0):
        Block.__init__(self, [input_variable], [output_variable], 1, 0)
        self.value = value
        self.offset = offset

    def Evaluate(self, it, ts):
        return self.value*self.InputValues(it)[0]+self.offset

    def LabelBlock(self):
        return str(self.value)

    def LabelConnections(self):
        return ['', '']


class Sum(Block):
    """Defines a sum over its inputs.

    .. math:: output = \sum{input_i}
       
    Args: 
        input_variable (list[Variables]): This is the list of inputs of the block.
        output_variable (Variable): This is the output of the block.

    """

    def __init__(self, inputs, output_variable):
        Block.__init__(self, inputs, [output_variable], 1, 0)

    def Evaluate(self, it, ts):
        return np.array([np.sum(self.InputValues(it))])

    def LabelBlock(self):
        return '+'

    def LabelConnections(self):
        return ['+', '+']


class WeightedSum(Block):
    """Defines a weighted sum over its inputs.

    .. math:: output = \sum{w_i \\times input_i}

    Args:        
        input_variable (list[Variables]): This is the list of inputs of the block.
        output_variable (Variable): This is the output of the block.
        weights: These are the weights that are multiplied by the elements of the input.
        offset: This offset is added to the final result.

    """

    def __init__(self, inputs, output_variable, weights, offset=0):
        Block.__init__(self, inputs, [output_variable], 1, 0)
        self.weights = weights
        self.offset = offset

    def Evaluate(self, it, ts):

        value = np.dot(self.weights, self.InputValues(it))+self.offset
        return value

    def LabelBlock(self):
        return 'W+'+str(self.weights)

    def LabelConnections(self):
        return self.weights


class Subtraction(Block):
    """Defines a subtraction between its two inputs.

    .. math:: output = input_1 - input_2
        
    Args:
        input_variable1 (Variable): This is the first input of the block, the minuend.
        input_variable2 (Variable): This is the second input of the block, the subtrahend.
        output_variable (Variable): This is the output of the block, the difference.

    """

    def __init__(self, input_variable1, input_variable2, output_variable):
        Block.__init__(self, [input_variable1, input_variable2], [
                       output_variable], 1, 0)

    def Evaluate(self, it, ts):
        return np.dot(np.array([1, -1]), self.InputValues(it))

    def LabelBlock(self):
        return '-'

    def LabelConnections(self):
        return ['+', '-']


class Product(Block):
    """Defines a multiplication between its inputs.

    .. math:: output = input_1 \\times input_2
        
    Args:
        input_variable1 (Variable): This is the first input of the block, one factor.
        input_variable2 (Variable): This is the second input of the block, another factor.
        output_variable (Variable): This is the output of the block, the product.

    """

    def __init__(self, input_variable1, input_variable2, output_variable):

        Block.__init__(self, [input_variable1, input_variable2], [
                       output_variable], 1, 0)

    def Evaluate(self, it, ts):
        value1, value2 = self.InputValues(it)
        return np.array([value1*value2])

    def LabelBlock(self):
        return 'x'

    def LabelConnections(self):
        return ['', '']


class Division(Block):
    """Defines a division between its inputs.

    .. math:: output = \\frac{input1}{input2}
    
    Args:    
        input_variable1 (Variable): This is the first input of the block, the dividend.
        input_variable2 (Variable): This is the second input of the block, the divisor.
        output_variable (Variable): This is the output of the block, the quotient.

    """

    def __init__(self, input_variable1, input_variable2, output_variable):

        Block.__init__(self, [input_variable1, input_variable2], [
                       output_variable], 1, 0)

    def Evaluate(self, it, ts):

        value1, value2 = self.InputValues(it)
        return value1 / value2

    def LabelBlock(self):
        return '/'

    def LabelConnections(self):
        return ['', '']


class ODE(Block):
    """Defines an ordinary differential equation based on the input.

    a, b are vectors of coefficients so that H, the transfer function of
    the block, can be written as:

    .. math:: H(p) = \\frac{a_i p^i}{b_j p^j}

    with Einstein sum on i and j, and p is Laplace's variable.

    For example, :code:`a=[1], b=[0,1]` is an integration, 
    and :code:`a=[0,1], b=[1]` is a differentiation.
        
    Args:
        input_variable (Variable): This is the input of the block.
        output_variable (Variable): This is the output of the block.
        a: This is the a vector for the transfer function.
        b: This is the b vector for the transfer function.

    """

    def __init__(self, input_variable, output_variable, a, b):
        Block.__init__(self, [input_variable], [
                       output_variable], len(a), len(b)-1)
#        self.AddInput(input_variable)
#        self.AddOutput(output_variable)
        self.a = a
        self.b = b
        self._M = {}  # Output matrices stored for differents time steps

    def _get_M(self, delta_t):
        n = len(self.a)
        A = np.zeros(n)
        for i, ai in enumerate(self.a):
            Ae = [self.a[i] * (-1)**j * factorial(i) / factorial(j) / factorial(
                i-j) / ((delta_t)**i) for j in range(i + 1)]  # Elementary A to assemblate in A
            for j, aej in enumerate(Ae):
                A[j] += aej

        n = len(self.b)
        B = np.zeros(n)
        for i, ai in enumerate(self.b):
            Be = [self.b[i] * (-1)**j * factorial(i) / factorial(j) / factorial(
                i-j) / ((delta_t)**i) for j in range(i + 1)]  # Elementary B to assemblate in B
            for j, bej in enumerate(Be):
                B[j] += bej

        Mo = [-x/B[0] for x in B[1:][::-1]]
        Mi = [x/B[0] for x in A[::-1]]
        return (Mi, Mo)

    def OutputMatrices(self, delta_t):
        try:
            Mi, Mo = self._M[delta_t]
        except KeyError:
            Mi, Mo = self._get_M(delta_t)
            self._M[delta_t] = (Mi, Mo)
        return Mi, Mo

    def Evaluate(self, it, ts):

        Mi, Mo = self.OutputMatrices(ts)
        # Solve at time t with time step ts
#        print(Mi,Mo)
#        print(np.dot(Mi,self.InputValues(it).T)+np.dot(Mo,self.OutputValues(it).T))
#        if abs(np.dot(Mi,self.InputValues(it).T)+np.dot(Mo,self.OutputValues(it).T))>10000:
#        print(Mi,self.InputValues(it),Mo,self.OutputValues(it))
#            print(np.dot(Mi,self.InputValues(it).T))
#            print(np.dot(Mo,self.OutputValues(it).T))
        return np.dot(Mi, self.InputValues(it).T) + np.dot(Mo, self.OutputValues(it).T)

    def LabelBlock(self):
        return str(self.a) + '\n' + str(self.b)

    def LabelConnections(self):
        return ['', '']


class IntegrationBlock(ODE):
    """Creates an ODE block that performs integration of the input over time.
    
    .. math:: output = \int_{0}^{t} input\ dt
    
    Args:
        input_variable: This is the input or list of inputs of the block.
        output_variable (Variable): This is the output of the block.

    """
    def __init__(self, input_variable, output_variable):
        ODE.__init__(self, input_variable, output_variable, a=[1], b=[0, 1])
        
    def LabelBlock(self):
        return 'Integral'

    
class DifferentiationBlock(ODE):
    """Creates an ODE block that performs differentation of the input relative to time.
        
    .. math:: output = \\frac{d[input]}{dt}
    
    Args:
        input_variable: This is the input or list of inputs of the block.
        output_variable (Variable): This is the output of the block.
    
    """
    def __init__(self, input_variable, output_variable):
        ODE.__init__(self, input_variable, output_variable, a=[0, 1], b=[1])
        
    def LabelBlock(self):
        return 'dx/dt'


class FunctionBlock(Block):
    """This defines a custom function over the input(s).

    .. math:: output = f(input)
        
    Args:
        input_variable: This is the input or list of inputs of the block.
        output_variable (Variable): This is the output of the block.
        function: This is the function that takes the inputs and returns the output.

    """

    def __init__(self, input_variable, output_variable, function):
        self.list_as_input = isinstance(input_variable, list)

        if self.list_as_input:
            Block.__init__(self, input_variable, [output_variable], 1, 0)
        else:
            Block.__init__(self, [input_variable], [output_variable], 1, 0)

        self.function = function

    def Evaluate(self, it, ts):
        if self.list_as_input:
            return np.array([self.function(*self.InputValues(it))])
        else:
            return np.array([self.function(self.InputValues(it)[0])])

    def LabelBlock(self):
        return 'f(t)'

    def LabelConnections(self):
        return ['', '']


# class Switch(Block):
#    def __init__(self,input_variable,output_variable,function):
#        """
#            output=f(input)
#        """
#        Block.__init__(self,[input_variable],[output_variable],1,0)
#        self.function=function
#
#    def Evaluate(self,it,ts):
#        self.outputs[0]._values[it]=self.function(self.InputValues(it)[0])
#
#    def Label(self):
#        return 'f(t)'
