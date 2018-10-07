# -*- coding: utf-8 -*-

"""
Collection of mathematical function signals
"""

from bms import Signal
import numpy as np


class Step(Signal):
    """Create a Step with a certain amplitude, time delay and offset.

    .. math:: f(t) = amplitude \\times u(t - delay) + offset

    where

    .. math::
        u(t) =
        \\begin{cases}
            0, & \\textrm{if } t < 0

            1, & \\textrm{if } t \\geq 0
        \\end{cases}
        

    Args:
        name (str): The name of this signal.
        amplitude: The height of the step function.
        delay: The time to wait before the function stops being zero.
        offset: The vertical offset of the function.

    """

    def __init__(self, name='Step', amplitude=1, delay=0, offset=0):
        Signal.__init__(self, name)

        def function(t):
            if t < delay:
                return offset
            else:
                return amplitude + offset
        self.function = function


class Ramp(Signal):
    """Create a Ramp with a certain amplitude, time delay and offset.

    .. math:: f(t) = amplitude \\times (t - delay) + offset

    Args:
        name (str): The name of this signal.
        amplitude: The angular coefficient of the Ramp function.
        delay: The horizontal offset of the function.
        offset: The vertical offset of the function.

    """

    def __init__(self, name='Ramp', amplitude=1, delay=0, offset=0):
        Signal.__init__(self, name)

        def function(t):
            if t < delay:
                return offset
            else:
                return (t-delay) * amplitude + offset
        self.function = function

unit_ramp = Ramp(amplitude = 1, name='Unit ramp')

class Sinus(Signal):
    """Create a Sine wave with a certain amplitude, angular velocity, phase and offset.

    .. math:: f(t) = amplitude \\times sin(\\omega \\times t + phase) + offset

    Args:
        name (str): The name of this signal.
        amplitude: The amplitude of the sine wave.
        w: The angular velocity of the sine wave (:math:`\\omega`).
        phase: The phase of the sine wave.
        offset: The vertical offset of the function.

    """
    def __init__(self, name='Sinus', amplitude=1, w=1, phase=0, offset=0):
        Signal.__init__(self, name)
        self.function = lambda t: amplitude * np.sin(w * t + phase) + offset


class SignalFunction(Signal):
    """Create a signal based on a function defined by the user.

    Args:
        name (str): The name of this signal.
        function: A function that depends on time.

    """

    def __init__(self, name, function):
        Signal.__init__(self, name)
        self.function = function
