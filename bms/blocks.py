# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 14:28:38 2015

@author: steven
"""

from bms import *

class Gain(Block):
    def __init__(self,input_variable,output_variable,value):
        """
            output=value* input    
        """
        Block.__init__(self,[input_variable],[output_variable],1,0)
        self.value=value

    def Solve(self,it,ts):
        self.outputs[0]._values[it]=self.value*self.InputValues(it)[0]
        
    def Label(self):
        return str(self.value)


class Sum(Block):
    def __init__(self,input_variable1,input_variable2,output_variable):
        """
            output=input1+input2    
        """
        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)

    def Solve(self,it,ts):
        self.outputs[0]._values[it]=np.dot(np.ones(2),self.InputValues(it))

    def Label(self):
        return '+'
        
class Subtraction(Block):
    def __init__(self,input_variable1,input_variable2,output_variable):
        """
            output=input1-input2    
        """
        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)

    def Solve(self,it,ts):
        self.outputs[0]._values[it]=np.dot(np.array([1,-1]),self.InputValues(it))   
        
    def Label(self):
        return '-'
        
class Product(Block):
    def __init__(self,input_variable1,input_variable2,output_variable):
        """
            output=input1*input2    
        """
        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)

    def Solve(self,it,ts):
        value1,value2=self.InputValues(it)
        self.outputs[0]._values[it]=value1*value2

    def Label(self):
        return 'x'

class Division(Block):
    def __init__(self,input_variable1,input_variable2,output_variable):
        """
            output=input1/input2    
        """
        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)

    def Solve(self,it,ts):
        value1,value2=self.InputValues(it)
        self.outputs[0]._values[it]=value1/value2

    def Label(self):
        return '/'

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
    def __init__(self,input_variable,output_variable,min_value,max_value):
        """
            output=min_value if input < min_value
            output=max_value if input > max_value
            output=input if  min_value < input < max_value
            
        """
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
        
    def Label(self):
        return 'min<x<max'

class Coulomb(Block):
    def __init__(self,input_variable,speed_variable,output_variable,max_value,tolerance=0):
        """
            Return coulomb force under condition of speed and sum of forces (input)
            
        """
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
        
    def Label(self):
        return 'Clb'
    
    
class ODE(Block):
    def __init__(self,input_variable,output_variable,a,b):
        """4
        a,b are vectors of coefficients such as H, the transfert function of
            the block, may be written as:
            H(p)=(a[i]p**i)/(b[j]p**j) (Einstein sum on i,j)
            p is Laplace's variable 
        """
        Block.__init__(self,[input_variable],[output_variable],len(a),len(b)-1)
#        self.AddInput(input_variable)
#        self.AddOutput(output_variable)
        self.a=a
        self.b=b
        self._M={}# Output matrices stored for differents time steps


    def _get_M(self,delta_t):
        n=len(self.a)
        A=np.zeros(n)
        for i,ai in enumerate(self.a):
            Ae=[self.a[i]*(-1)**j*math.factorial(i)/math.factorial(j)/math.factorial(i-j)/((delta_t)**i) for j in range(i+1)]# Elementery A to assemblate in A
            for j,aej in enumerate(Ae):
                A[j]+=aej

        n=len(self.b)
        B=np.zeros(n)
        for i,ai in enumerate(self.b):
            Be=[self.b[i]*(-1)**j*math.factorial(i)/math.factorial(j)/math.factorial(i-j)/((delta_t)**i) for j in range(i+1)]# Elementery A to assemblate in A
            for j,bej in enumerate(Be):
                B[j]+=bej
                
        Mo=[-x/B[0] for x in B[1:][::-1]]
        Mi=[x/B[0] for x in A[::-1]]
        return (Mi,Mo)
            
    def OutputMatrices(self,delta_t):
        try:
            Mi,Mo=self._M[delta_t]
        except KeyError:
            Mi,Mo=self._get_M(delta_t)
            self._M[delta_t]=(Mi,Mo)
        return Mi,Mo
        
    def Solve(self,it,ts):
        Mi,Mo=self.OutputMatrices(ts)
        # Solve at time t with time step ts
        self.outputs[0]._values[it]=np.dot(Mi,self.InputValues(it).T)+np.dot(Mo,self.OutputValues(it).T)
        
    def Label(self):
        return str(self.a)+'\n'+str(self.b)
        
class FunctionBlock(Block):
    def __init__(self,input_variable,output_variable,function):
        """
            output=f(input)    
        """
        Block.__init__(self,[input_variable],[output_variable],1,0)
        self.function=function

    def Solve(self,it,ts):
        self.outputs[0]._values[it]=self.function(self.InputValues(it)[0])

    def Label(self):
        return 'f(t)'
        
