# -*- coding: utf-8 -*-
"""
Core of BMS. All content of this file is imported by bms, and is therefore in bms

This file defines the base of BMS. 

"""

import numpy as np
import matplotlib.pyplot as plt
import math
import networkx as nx
import dill

class Variable:
    """ Defines a variable
    
    :param names: Defines full name and short name.
    If names is a string the two names will be identical
    otherwise names should be a tuple of strings (full_name,short_name) 
    
    """    
    def __init__(self,names='',initial_values=[0]):
        if type(names)==str:
            self.name=names
            self.short_name=names 
        else:
            try:
                self.short_name=names[1]
                self.name=names[0]
            except:
                raise TypeError
                
        self.initial_values=initial_values
        self._values=np.array([])
        self.max_order=0
    
    def _InitValues(self,ns,ts,max_order):
        self.max_order=max_order
        self._values=np.zeros(ns+max_order+1)
        self._ForwardValues()
            
    def _ForwardValues(self):
        pass
    
    def _get_values(self):
        return self._values[self.max_order:]
    
    values=property(_get_values)
    
        
class Signal(Variable):
    """ Abstract class of signal """
    def __init__(self,names):
        if type(names)==str:
            self.name=names
            self.short_name=names 
        else:
            try:
                self.short_name=names[1]
                self.name=names[0]
            except:
                raise TypeError
            
        self._values=np.array([])
        self.max_order=0
        
        
    def _InitValues(self,ns,ts,max_order):
        self.max_order=max_order
        self._values=np.zeros(ns+max_order+1)
        for i in range(ns+1):
            self._values[i+max_order]=self.function(i*ts)
        self._ForwardValues()
            
    def _ForwardValues(self):
        pass

    

class Block:
    """ Abstract class of block: this class should not be instanciate directly
    """
    def __init__(self,inputs,outputs,max_input_order,max_output_order):
        self.inputs=[]
        self.outputs=[]        

        self.n_inputs=len(inputs)
        self.n_outputs=len(outputs)
        

        for variable in inputs:
            self._AddInput(variable)
        for variable in outputs:
            self._AddOutput(variable)
            
#        self.input_orders=
#        self.output_orders=output_orders
        self.max_input_order=max_input_order
        self.max_output_order=max_output_order
        self.max_order=max(self.max_input_order,self.max_output_order)
        
    def _AddInput(self,variable):
        """
        Add one more variable as an input of the block
        
        :param variable: variable (or signal as it is also a variable)
        """
        if isinstance(variable,Variable):
            self.inputs.append(variable)
        else:
            print('Error: ',variable.name,variable,' given is not a variable')
            raise TypeError

    def _AddOutput(self,variable):
        """
            Add one more variable as an output of the block
            
            :param variable: variable (or signal as it is also a variable)
        """
        if isinstance(variable,Variable):
            self.outputs.append(variable)
        else:
            raise TypeError

    def InputValues(self,it):
        """
            Returns the input values at a given iteration for solving the block outputs
        """
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
    """
    Defines a dynamic system that can simulate itself
    
    :param te: time of simulation's end 
    :param ns: number of steps
    :param blocks: (optional) list of blocks defining the model        
        
    """
    def __init__(self,te,ns,blocks=[]):
        self.te=te
        self.ns=ns
        self.ts=self.te/float(self.ns)# time step
        self.t=np.linspace(0,self.te,num=ns+1)# Time vector
        self.blocks=[]
        self.variables=[]
        self.signals=[]

        self.max_order=0        
        
        for block in blocks:
            self.AddBlock(block)
        
        self._utd_graph=False# True if graph is up-to-date
        
    def AddBlock(self,block):
        """
        Add the given block to the model and also its input/output variables
        """
        if isinstance(block,Block):
            self.blocks.append(block)
            self.max_order=max(self.max_order,block.max_input_order-1)
            self.max_order=max(self.max_order,block.max_output_order)
            for variable in block.inputs+block.outputs:
                self._AddVariable(variable)
        else:
            raise TypeError
        self._utd_graph=False
        
    def _AddVariable(self,variable):
        """
        Add a variable to the model. Should not be used by end-user
        """
        if isinstance(variable,Signal):
            if not variable in self.variables:
                self.signals.append(variable)
        elif isinstance(variable,Variable):
            if not variable in self.variables:
                self.variables.append(variable)
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
    
        
    def _ResolutionOrder(self):
        """
        Finds the blocks resolution order. Should not be used by end-user
        """
        known_variables=self.signals[:]
        resolution_order=[]
        half_known_variables=[]
        half_solved_blocks={}
        unsolved_blocks=self.blocks[:]
        graph_loops=list(nx.simple_cycles(self.graph))
#        print(graph_loops)
        while len(known_variables)<(len(self.variables)+len(self.signals)):
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
        for variable in self.signals:
            if self.graph.predecessors(variable)!=[]:
                raise ModelError
        for variable in self.variables:
            if len(self.graph.predecessors(variable))>1:
                raise ModelError
                            
    def Simulate(self):
        self.CheckModelConsistency()
        resolution_order=self._ResolutionOrder()
        # Initialisation of variables values
        for variable in self.variables+self.signals:
#            if not isinstance(variable,Input):
            variable._InitValues(self.ns,self.ts,self.max_order)
#            else:
#                variable.Values(self.ns,self.ts,self.max_order)
        for it,t in enumerate(self.t[1:]):           
#            print('iteration step/time: ',it,t,'/',it+self.max_order+1)
            for block in resolution_order:
#                print('write @ ',it+self.max_order)
                block.Solve(it+self.max_order+1,self.ts)
#                print(block)

    def VariablesValues(self,variables,t): 
        """
        Returns the value of given variables at time t
        
        :param variables: one variable or a list of variables
        :param t: time of evaluation
        """                
        if (t<self.te)|(t>0):
            i=t//self.ts#time step            
            ti=self.ts*i
            if type(variables)==list:
                values=[]
                for variable in variables:
                    # interpolation
                    values.append(variables.values[i]*((ti-t)/self.ts+1)+variables.values[i+1]*(t-ti)/self.ts)
                return values

            else:
                # interpolation
                return variables.values[i]*((ti-t)/self.ts+1)+variables.values[i+1]*(t-ti)/self.ts
        else: raise ValueError
        
    def PlotVariables(self,subplots_variables=None):
        if subplots_variables==None:
            subplots_variables=[self.signals+self.variables]
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
        from .interface import ModelDrawer
        ModelDrawer(self)

    def Save(self,name_file):
        """
            name_file: name of the file without extension.
            The extension .bms is added by function
        """
        with open(name_file+'.bms','wb') as file:
            model=dill.dump(self,file)
        

    def __getstate__(self):
        dic = self.__dict__.copy()        
        return dic
        
    def __setstate__(self,dic):
        self.__dict__ = dic        
        
def Load(file):
    """ Loads a model from specified file """
    with open(file,'rb') as file:
        model=dill.load(file)
        return model
