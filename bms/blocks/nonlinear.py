# -*- coding: utf-8 -*-
"""
Collection of non-linear blocks

"""

from bms import Block
from numpy import array

#class DeadZone(Block):
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


#class Hysteresis(Block):
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

    
#class Delay(Block):
#    def __init__(self,input_variable,output_variable,delay):
#        Block.__init__(self,[input_variable],[output_variable],1,0)
#        self.delay=delay
#
#    def Evaluate(self,it,ts):
#        value1,value2=self.InputValues(it)
#        self.outputs[0]._values[it]=value1/value2
#
#    def Label(self):
#        return 'dly'

        
class Saturation(Block):
    """
        output=min_value if input < min_value
        output=max_value if input > max_value
        output=input if  min_value < input < max_value        
    """
    def __init__(self,input_variable,output_variable,min_value,max_value):
        Block.__init__(self,[input_variable],[output_variable],1,0)
        self.min_value=min_value
        self.max_value=max_value

    def Evaluate(self,it,ts):
        value=self.InputValues(it)[0]
        if value<self.min_value:
            value=self.min_value
        elif value>self.max_value:
            value=self.max_value
        return array([value])
        
    def LabelBlock(self):
        return 'Sat'
        

class Coulomb(Block):
    """
        Return coulomb force under condition of speed and sum of forces (input)
        
    """
    def __init__(self,input_variable,speed_variable,output_variable,max_value,tolerance=0):
        Block.__init__(self,[input_variable,speed_variable],[output_variable],1,0)
        self.max_value=max_value
        self.tolerance=tolerance

    def Evaluate(self,it,ts):
        input_value,speed=self.InputValues(it)
        if speed>self.tolerance:
            output=-self.max_value
        elif speed<-self.tolerance:
            output=self.max_value
        else:
            if abs(input_value)<self.max_value:
                output=-input_value
            else:
                if input_value<0:
                    output=self.max_value
                else:
                    output=-self.max_value
                    
        return array([output])
        
    def LabelBlock(self):
        return 'Clb'

class CoulombVariableValue(Block):
    """
        Return coulomb force under condition of speed and sum of forces (input)
        The max value is driven by an input
    """
    def __init__(self,external_force,speed_variable,value_variable,output_variable,tolerance=0):
        Block.__init__(self,[external_force,speed_variable,value_variable],[output_variable],1,0)
#        self.max_value=max_value
        self.tolerance=tolerance

    def Evaluate(self,it,ts):
        external_force,speed,max_value=self.InputValues(it)
        # Slipping
        if speed>self.tolerance:
            output=-max_value
        elif speed<-self.tolerance:
            output=max_value
        else:
            # locked
            if abs(external_force)<max_value:
                # equilibrium
                output=-external_force
            else:
                # Breaking equilibrium
                if external_force<0:
                    output=max_value
                else:
                    output=-max_value
        return output
        
    def LabelBlock(self):
        return 'Clb Var'
    
class RegCoulombVariableValue(Block):
    """
        Return coulomb force under condition of speed and sum of forces (input)
        The max value is driven by an input
    """
    def __init__(self,external_force,speed_variable,value_variable,output_variable,tolerance=0):
        Block.__init__(self,[external_force,speed_variable,value_variable],[output_variable],1,0)
#        self.max_value=max_value
        self.tolerance=tolerance

    def Evaluate(self,it,ts):
        external_force,speed,max_value=self.InputValues(it)
        # Slipping
        if speed>self.tolerance:
            output=-max_value
        elif speed<-self.tolerance:
            output=max_value
        else:
            # locked
            if abs(external_force)<max_value:
                # equilibrium
                output=-external_force
            else:
                # Breaking equilibrium
                if external_force<0:
                    output=max_value
                else:
                    output=-max_value
        return output
        
    def LabelBlock(self):
        return 'Clb Var'



class Sign(Block):
    """
        Return the sign of a variable
        :returns: * -1 if input < 0
                  *  1 if input > 0
        
    """
    def __init__(self,input_variable,output_variable):
        Block.__init__(self,[input_variable],[output_variable],1,0)

    def Evaluate(self,it,ts):
        input_value=self.InputValues(it)[0]
        if input_value<0:
            output=-1
        elif input_value>0:
            output=1            
        else:
            output=0
#        print(input_value,speed,output)
        return array([output])
        
    def LabelBlock(self):
        return 'Sgn'
