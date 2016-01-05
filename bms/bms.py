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
    def __init__(self,name='',initial_values=[0]):
        self.name=name
        self.initial_values=initial_values
        self._values=np.array([])
        self.max_order=0
    
    def InitValues(self,ns,ts,max_order):
        self.max_order=max_order
        self._values=np.zeros(ns+max_order+1)
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
        self._values=np.zeros(ns+max_order+1)
        for i in range(ns+1):
            self._values[i+max_order]=self.function(i*ts)
        self.ForwardValues()
            
    def ForwardValues(self):
        pass



                
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
            print('Error: ',variable.name,variable,' given is not a variable')
            raise TypeError

    def AddOutput(self,variable):
        if isinstance(variable,Variable):
            self.outputs.append(variable)
        else:
            raise TypeError

    def InputValues(self,it):
#        print(self,it)
        # Provides values in inputs values for computing at iteration it
        I=np.zeros((self.n_inputs,self.max_input_order))
        for iv,variable in enumerate(self.inputs):
#            print(it-self.max_input_order+1,it+1)            
#            print(variable._values[it-self.max_input_order+1:it+1])
            I[iv,:]=variable._values[it-self.max_input_order+1:it+1]
        return I
            
    def OutputValues(self,it):
        # Provides values in inputs values for computing at iteration it
        O=np.zeros((self.n_outputs,self.max_output_order))
        for iv,variable in enumerate(self.outputs):
            O[iv,:]=variable._values[it-self.max_output_order:it]
        return O

class ModelError(Exception):
    def __init__(self):
        pass
    
    def __str__(self):
        return 'Model Error'
            
        
class DynamicSystem:
    def __init__(self,te,ns,blocks=[]):
        """
        te: time of simulation's end 
        ns: number of steps
        
        """
        self.te=te
        self.ns=ns
        self.ts=self.te/(self.ns)# time step
        self.t=np.linspace(0,self.te,num=ns+1)# Time vector
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
                solved_input_variables=[]
                half_solved_input_variables=[]
                unsolved_input_variables=[]
                for variable in block.inputs:
                    if variable in known_variables:
                        solved_input_variables.append(variable)
                    elif variable in half_known_variables:
                        half_solved_input_variables.append(variable)
                    else:
                        unsolved_input_variables.append(variable)
                        
                
                if unsolved_input_variables==[]:
                    if solved_input_variables!=[]:
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
                    if score>max_score_block:
                        scores[block]=score
                if scores!={}:
                    max_score=0
                    for block,score in scores.items():
                        if score>max_score:
                            max_score=score
                            max_block=block
                            
                    # Half solve block
                    resolution_order.append(max_block)
                    half_solved_blocks[max_block]=max_score
                    for variable in max_block.outputs:
                        if not variable in known_variables+half_known_variables:
                            half_known_variables.append(variable)

                else:
                    raise NotImplemented
                    
                             
        return resolution_order 
        
        
        
    def CheckModelConsistency(self):
        """
            Check for model consistency:
             - an input variable can't be set as the output of a block
             - a variable can't be the output of more than one block
             
        """
        for variable in self.inputs:
            if self.graph.predecessors(variable)!=[]:
                raise ModelError
        for variable in self.variables:
            if len(self.graph.predecessors(variable))>1:
                raise ModelError
                            
    def Simulate(self):
        self.CheckModelConsistency()
        resolution_order=self.ResolutionOrder()
        # Initialisation of variables values
        for variable in self.variables+self.inputs:
#            if not isinstance(variable,Input):
            variable.InitValues(self.ns,self.ts,self.max_order)
#            else:
#                variable.Values(self.ns,self.ts,self.max_order)
        for it,t in enumerate(self.t[1:]):           
#            print('iteration step/time: ',it,t,'/',it+self.max_order+1)
            for block in resolution_order:
#                print('write @ ',it+self.max_order)
                block.Solve(it+self.max_order+1,self.ts)
#                print(block)
                
    def PlotVariables(self,subplots_variables=None):
        if subplots_variables==None:
            subplots_variables=[self.variables]
#        plt.figure()
        fig,axs=plt.subplots(len(subplots_variables),sharex=True)
        if len(subplots_variables)==1:
            axs=[axs]
        for isub,subplot in enumerate(subplots_variables):
            legend=[]
            for variable in subplot:
                axs[isub].plot(self.t,variable.values)
                legend.append(variable.name)
            axs[isub].legend(legend,loc='best')
            axs[isub].margins(0.08)
            axs[isub].grid()
                            
        plt.xlabel('Time')
        fig.show()
        
    def DrawModel(self):
        f,ax=plt.subplots(1)
        labels={}
        for variable in self.variables:
            labels[variable]=variable.name
        for block in self.blocks:
            labels[block]=block.Label()
            
            
        position=nx.spectral_layout(self.graph)
        # Drawing blocks
        nx.draw_networkx_nodes(self.graph,position,ax=ax,nodelist=self.blocks,node_color='grey',node_shape='s',node_size=1200)
        # Drawing variable
        nx.draw_networkx_nodes(self.graph,position,ax=ax,nodelist=self.variables,node_color='white',node_size=800)
        nx.draw_networkx_labels(self.graph,position,labels,ax=ax,font_size=16)
        nx.draw_networkx_edges(self.graph,position)
        plt.show()
