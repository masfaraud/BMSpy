# -*- coding: utf-8 -*-
"""
Collection of continuous blocks

"""


#from ..blocks import Block
from bms import Block,np,math


class Gain(Block):
    """
        output=value* input    
    """
    def __init__(self,input_variable,output_variable,value):
        Block.__init__(self,[input_variable],[output_variable],1,0)
        self.value=value

    def Solve(self,it,ts):
        self.outputs[0]._values[it]=self.value*self.InputValues(it)[0]
        
    def LabelBlock(self):
        return str(self.value)

    def LabelConnections(self):
        return ['','']


class Sum(Block):
    """
        output=input1+input2    
    """
    def __init__(self,input_variable1,input_variable2,output_variable):
        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)

    def Solve(self,it,ts):
        self.outputs[0]._values[it]=np.dot(np.ones(2),self.InputValues(it))

    def LabelBlock(self):
        return ''

    def LabelConnections(self):
        return ['+','+']

class Subtraction(Block):
    """
        output=input1-input2    
    """
    def __init__(self,input_variable1,input_variable2,output_variable):
        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)

    def Solve(self,it,ts):
        self.outputs[0]._values[it]=np.dot(np.array([1,-1]),self.InputValues(it))   
        
    def LabelBlock(self):
        return ''

    def LabelConnections(self):
        return ['+','-']

        
class Product(Block):
    """
        output=input1*input2    
    """
    def __init__(self,input_variable1,input_variable2,output_variable):

        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)

    def Solve(self,it,ts):
        value1,value2=self.InputValues(it)
        self.outputs[0]._values[it]=value1*value2

    def LabelBlock(self):
        return 'x'

    def LabelConnections(self):
        return ['','']

class Division(Block):
    """
        output=input1/input2    
    """
    def __init__(self,input_variable1,input_variable2,output_variable):

        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)

    def Solve(self,it,ts):
        value1,value2=self.InputValues(it)
        self.outputs[0]._values[it]=value1/value2

    def LabelBlock(self):
        return '/'

    def LabelConnections(self):
        return ['','']

    
    
class ODE(Block):
    """
        a,b are vectors of coefficients such as H, the transfert function of
        the block, may be written as:
        H(p)=(a[i]p**i)/(b[j]p**j) (Einstein sum on i,j)
        p is Laplace's variable 
    """
    def __init__(self,input_variable,output_variable,a,b):
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
        
    def LabelBlock(self):
        return str(self.a)+'\n'+str(self.b)

    def LabelConnections(self):
        return ['','']
        
        
class FunctionBlock(Block):
    """
        output=f(input)    
    """
    def __init__(self,input_variable,output_variable,function):

        Block.__init__(self,[input_variable],[output_variable],1,0)
        self.function=function

    def Solve(self,it,ts):
        self.outputs[0]._values[it]=self.function(self.InputValues(it)[0])

    def LabelBlock(self):
        return 'f(t)'
        
    def LabelConnections(self):
        return ['','']
        
        
#class Switch(Block):
#    def __init__(self,input_variable,output_variable,function):
#        """
#            output=f(input)    
#        """
#        Block.__init__(self,[input_variable],[output_variable],1,0)
#        self.function=function
#
#    def Solve(self,it,ts):
#        self.outputs[0]._values[it]=self.function(self.InputValues(it)[0])
#
#    def Label(self):
#        return 'f(t)'
