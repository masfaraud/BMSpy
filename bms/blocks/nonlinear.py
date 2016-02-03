# -*- coding: utf-8 -*-
"""
Collection of non-linear blocks

"""

from bms import Block

class DeadZone(Block):
    """
        
    """
    def __init__(self,input_variable,output_variable,zone_width):
        Block.__init__(self,[input_variable,trigger_variable],[output_variable],1,0)
        self.zone_width=zone_width

    def Solve(self,it,ts):
        input_value=self.InputValues(it)[0]
        if value<-0.5*self.zone_width:
            output=value+0.5*self.zone_width
        elif value>-0.5*self.zone_width:
            output=value-0.5*self.zone_width
        else:
            output=0
        self.outputs[0]._values[it]=output


class Hysteresis(Block):
    """

    """
    def __init__(self,input_variable,output_variable,zone_width,initial_value):
        Block.__init__(self,[input_variable,trigger_variable],[output_variable],1,0)
        self.zone_width=zone_width
        self.value=initial_value

    def Solve(self,it,ts):
        input_value=self.InputValues(it)[0]
        if self.value>input_value+0.5*self.zone_width:
            output=input_value+0.5*self.zone_width
            self.value=output
        elif self.value<input_value-0.5*self.zone_width:
            output=input_value-0.5*self.zone_width
            self.value=output
        self.outputs[0]._values[it]=output

    
#class Delay(Block):
#    def __init__(self,input_variable,output_variable,delay):
#        Block.__init__(self,[input_variable],[output_variable],1,0)
#        self.delay=delay
#
#    def Solve(self,it,ts):
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

    def Solve(self,it,ts):
        value=self.InputValues(it)[0]
        if value<self.min_value:
            value=self.min_value
        elif value>self.max_value:
            value=self.max_value
        self.outputs[0]._values[it]=value
        
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

    def Solve(self,it,ts):
        input_value,speed=self.InputValues(it)
        if speed>self.tolerance:
            output=-self.max_value
        elif speed<-self.tolerance:
            output=self.max_value
        else:
            if abs(input_value)<self.max_value:
                output=input_value
            else:
                output=self.max_value
#        print(input_value,speed,output)
        self.outputs[0]._values[it]=output
        
    def LabelBlock(self):
        return 'Clb'
