# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 18:23:50 2015

@author: Steven Masfaraud
"""

import numpy as np
import matplotlib.pyplot as plt
import math
import networkx as nx

class Variable:
    def __init__(self,name='',initial_value=0,derivatives=[]):
        self.name=name
        self.initial_value=initial_value
        self._values=np.array([])
        self.derivatives=derivatives
        self.max_order=0
    
    def InitValues(self,ns,ts,max_order):
        self.max_order=max_order
        self._values=np.zeros(ns+max_order)
        self.ForwardValues()
            
    def ForwardValues(self):
        pass
    
    def _get_values(self):
        return self._values[self.max_order:]
    
    values=property(_get_values)
    
        
class Input(Variable):
    def __init__(self,name):
        self.name=name
        self._values=np.array([])
        self.max_order=0
        
        
    def InitValues(self,ns,ts,max_order):
        self.max_order=max_order
        self._values=np.zeros(ns+max_order)
        for i in range(ns):
            self._values[i+max_order]=self.function(i*ts)
        self.ForwardValues()
            
    def ForwardValues(self):
        pass


class Step(Input):
    def __init__(self,value,name):
        Input.__init__(self,name)
        self.function=lambda x:value

class Ramp(Input):
    def __init__(self,value,name):
        Input.__init__(self,name)
        self.function=lambda x:x*value            
                
#class Output(Variable):
#    def __init__(self):
#        Variable.__init__(self)
    

class Block:
    def __init__(self,inputs,outputs,max_input_order,max_output_order):
        self.inputs=[]
        self.outputs=[]        

        self.n_inputs=len(inputs)
        self.n_outputs=len(outputs)
        

        for variable in inputs:
            self.AddInput(variable)
        for variable in outputs:
            self.AddOutput(variable)
            
#        self.input_orders=
#        self.output_orders=output_orders
        self.max_input_order=max_input_order
        self.max_output_order=max_output_order
        self.max_order=max(self.max_input_order,self.max_output_order)
        
    def AddInput(self,variable):
        if isinstance(variable,Variable):
            self.inputs.append(variable)
        else:
            raise TypeError

    def AddOutput(self,variable):
        if isinstance(variable,Variable):
            self.outputs.append(variable)
        else:
            raise TypeError

    def InputValues(self,it):
        # Provides values in inputs values for computing at iteration it
        I=np.zeros((self.n_inputs,self.max_input_order))
        for iv,variable in enumerate(self.inputs):
            I[iv,:]=variable._values[it-self.max_input_order+1:it+1]
        return I
            
    def OutputValues(self,it):
        # Provides values in inputs values for computing at iteration it
        O=np.zeros((self.n_outputs,self.max_output_order))
        for iv,variable in enumerate(self.outputs):
            O[iv,:]=variable._values[it-self.max_output_order:it]
        return O

class SumBlock(Block):
    def __init__(self,input_variable1,input_variable2,output_variable):
        """
            output=input1+input2    
        """
        Block.__init__(self,[input_variable1,input_variable2],[output_variable],1,0)
#        self.AddInput(input_variable)
#        self.AddOutput(output_variable)

    def Solve(it,ts):
        self.outputs[0]._values[it]=np.dot(np.ones(2),self.InputValues(it).T)
    
class ODEBlock(Block):
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
            
        
class DynamicSystem:
    def __init__(self,te,ns,blocks=[]):
        """
        te: time of simulation's end 
        ns: number of steps
        
        """
        self.te=te
        self.ns=ns
        self.ts=self.te/(self.ns-1)# time stem 
        self.t=np.arange(0,self.te+self.ts,self.ts)# Time vector
        self.blocks=[]
        self.variables=[]
        self.inputs=[]

        self.max_order=0        
        
        for block in blocks:
            self.AddBlock(block)
        
        self._utd_graph=False# True if graph is up-to-date
        
    def AddBlock(self,block):
        if isinstance(block,Block):
            self.blocks.append(block)
            self.max_order=max(self.max_order,block.max_input_order-1)
            self.max_order=max(self.max_order,block.max_output_order)
            for variable in block.inputs+block.outputs:
                self.AddVariable(variable)
        else:
            raise TypeError
        self._utd_graph=False
        
    def AddVariable(self,variable):
        if isinstance(variable,Variable):
            if not variable in self.variables:
                self.variables.append(variable)
                if isinstance(variable,Input):
                    self.inputs.append(variable)
        else:
            raise TypeError
        self._utd_graph=False

    def _get_Graph(self):
        if not self._utd_graph:
            # Generate graph
            self._graph=nx.DiGraph()
            for variable in self.variables:
                self._graph.add_node(variable)
            for block in self.blocks:
                self._graph.add_node(block)
                for variable in block.inputs:
                    self._graph.add_edge(variable,block)
                for variable in block.outputs:
                    self._graph.add_edge(block,variable)

            self._utd_graph=True
        return self._graph
                
        
    graph=property(_get_Graph)
    
    def DrawGraph(self):
        nx.draw(self.graph)
        
    def ResolutionOrder(self):
        known_variables=self.inputs[:]
        resolution_order=[]
        half_known_variables=[]
        half_solved_blocks={}
        unsolved_blocks=self.blocks[:]
        graph_loops=list(nx.simple_cycles(self.graph))
#        print(graph_loops)
        while len(known_variables)<len(self.variables):
            block_solved=False
            # Check if a block out of remaining is solvable
            # ie if all inputs are known of half known
            for block in unsolved_blocks:
                unsolved_input_variables=[]
#                solvable=1
                for variable in block.inputs:
                    if not variable in known_variables+half_known_variables:
                        unsolved_input_variables.append(variable)
                        
                
                if unsolved_input_variables==[]:
                    resolution_order.append(block)
                    unsolved_blocks.remove(block)
                    block_solved=True
                    for variable in block.outputs:
                        if not variable in known_variables:
                            known_variables.append(variable)
                    break
            if not block_solved:
                # A block with inputs partially can half solve its outputs
                
                # Each block is assigned a score
                # defined by the ratio of already knowns variables
                scores={}
                for block in unsolved_blocks:
                    score=0
                    # counting variables
                    for variable in block.inputs:
                        if variable in known_variables:
                            score+=2# helps propagating information
                        elif variable in half_known_variables:
                            score+=0.5
                        else:
                            # Variable not even half known.
                            # It has to be part of a loop to be solve                        
                            in_loop=False
                            for loop in graph_loops:
                                if (block in loop)&(variable in loop):
                                    in_loop=True
                            if not in_loop:
                                score=0
                                break
                    try:
                        max_score_block=half_solved_blocks[block]                                        
                    except:
                        max_score_block=0
                    print(half_solved_blocks)
                    if score>max_score_block:
                        scores[block]=score
                print(score)
                if scores!={}:
                    max_score=0
                    for block,score in scores.items():
                        if score>max_score:
                            max_score=score
                            max_block=block
                            
#                            max_loop=score_loop[1]
                    # Add loop in solvable blocks
                            
                    # Add
                else:
                    raise NotImplemented
                    
                # Half solve block
                resolution_order.append(max_block)
                half_solved_blocks[max_block]=max_score
                print(max_block)
                for variable in max_block.inputs:
                    if not variable in known_variables+half_known_variables:
                        half_known_variables.append(variable)
                            
        return resolution_order 
        
                            
    def Simulate(self):
        resolution_order=self.ResolutionOrder()
        # Initialisation of variables values
        for variable in self.variables+self.inputs:
#            if not isinstance(variable,Input):
            variable.InitValues(self.ns,self.ts,self.max_order)
#            else:
#                variable.Values(self.ns,self.ts,self.max_order)
        for it,t in enumerate(self.t):           
#            print('iteration step/time: ',it,t,'/',self.t.shape)
            for block in resolution_order:
#                print('write @ ',it+self.max_order)
                block.Solve(it+self.max_order,self.ts)
#                print(block)
                
    def PlotVariables(self,variables=None):
        if variables==None:
            variables=self.variables
        plt.figure()
        legend=[]
        for variable in variables:
            plt.plot(self.t,variable.values)
            legend.append(variable.name)
        plt.margins(self.te*0.03)
        plt.xlabel('Time')
        plt.legend(legend)
        plt.show()
            
                                    
