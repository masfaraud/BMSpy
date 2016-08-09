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
    :param hidden: inner variable to hide in plots if true
    """    
    def __init__(self,names='variable',initial_values=[0],hidden=False):
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
        self.hidden=hidden
    
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
        self.hidden=False
        
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
        self.ts=self.te/(self.ns)# time step
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
                    raise NotImplementedError
                    
                             
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
            subplots_variables=[[variable for variable in self.signals+self.variables if not variable.hidden]]
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

class PhysicalNode:
    """
    Abstract class
    """
    def __init__(self,node_name,potential_variable_name,flux_variable_name):
        self.name=node_name
        self.potential_variable_name=potential_variable_name
        self.flux_variable_name=flux_variable_name
        self.variable=Variable(potential_variable_name+' '+node_name)

class PhysicalBlock:
    """
    Abstract class to inherit when coding a physical block
    """
    def __init__(self,nodes,name):
        self.nodes=nodes
        self.name=name
        self.variables=[Variable(node.flux_variable_name+' from '+node.name+' to '+self.name) for node in nodes]
        
class PhysicalSystem:
    """
    Defines a physical system
    """
    def __init__(self,te,ns,physical_blocks):
        self.te=te
        self.ns=ns
        self.blocks=[]        
        self.nodes=[]
        for block in physical_blocks:
            self.AddBlock(block)
            
        self._utd_ds=False

    def AddBlock(self,block):
        if isinstance(block,PhysicalBlock):
            self.blocks.append(block)
            for node in block.nodes:
                self._AddNode(node)
        else:
            raise TypeError
        self._utd_ds=False
        
    def _AddNode(self,node):
        if isinstance(node,PhysicalNode):
            if not node in self.nodes:
                self.nodes.append(node)
        self._utd_ds=False        
        
    def GenerateDynamicSystem(self):
        from bms.blocks.continuous import WeightedSum
        G=nx.Graph()
#        variables={}
        # Adding node variables
        for node in self.nodes:
            G.add_node(node.variable,bipartite=0)
        for block in self.blocks:
            for variable in block.variables:
                # add variable realted to connection
                G.add_node(node.variable,bipartite=0)
            ne,nv=block.occurence_matrix.shape                
            # Add equations of blocs
            for ie in range(ne): 
                G.add_node((block,ie),bipartite=1)
                for iv in range(nv):
#                    print(iv)
                    if block.occurence_matrix[ie,iv]==1:
                        if iv%2==0:
                            G.add_edge((block,ie),block.nodes[iv//2].variable)
                        else:
                            G.add_edge((block,ie),block.variables[iv//2])
        # Adding equation of physical nodes: sum of incomming variables =0
        for node in self.nodes:
            G.add_node(node,bipartite=1)
            for block in self.blocks:
                for inb,node_block in enumerate(block.nodes):
                    if node==node_block:
                        G.add_edge(node,block.variables[inb])
                        
        pos=nx.spring_layout(G)
        nx.draw(G,pos) 
        nx.draw_networkx_labels(G,pos)
#        import matplotlib.pyplot as plt
#        plt.figure()
        G2=nx.DiGraph()
        G2.add_nodes_from(G)
        eq_out_var={}
#        print('=====================')
        for e in nx.bipartite.maximum_matching(G).items():
#            print(e[0].__class__.__name__)
            # eq -> variable
            if e[0].__class__.__name__=='Variable':              
                G2.add_edge(e[1],e[0])
                eq_out_var[e[1]]=e[0]                
            else:
                G2.add_edge(e[0],e[1])
                eq_out_var[e[0]]=e[1]
                
        for e in G.edges():
            if e[0].__class__.__name__=='Variable':                
                G2.add_edge(e[0],e[1])
            else:
                G2.add_edge(e[1],e[0])
#        print('@@@@@@@@@@@@@@@@@@@@@@@@')
#        pos=nx.spring_layout(G2)
#        nx.draw(G2,pos)       
#        nx.draw_networkx_labels(G2,pos)
        
        sinks=[]
        sources=[]    
        for node in G2.nodes():
            if G2.out_degree(node)==0:
                sinks.append(node)
            elif G2.in_degree(node)==0:
                sources.append(node)
#        print(sinks,sources)
        
        if (sinks!=[])|(sources!=[]):
            raise ModelError
            
        # Model is solvable: it must say to equations of blocks which is their 
        # output variable
        
#        print(eq_out_var)
        model_blocks=[]
        for block_node,variable in eq_out_var.items():
            print(block_node,variable)
            if type(block_node)==tuple:
                # Blocks writes an equation
                model_blocks.extend(block_node[0].PartialDynamicSystem(block_node[1],variable))
            else:
                # Sum of incomming variables at nodes
                # searching attached nodes
                variables=[]
                for block in self.blocks:
                    try:
                        ibn=block.nodes.index(block_node)
                        variable2=block.variables[ibn]
                        if variable2!=variable:
                            variables.append(variable2)
                    except:
                        ValueError
#                print('v: ',variables,variable)
#                v1=Variable()
                print('lv',len(variables))
                model_blocks.append(WeightedSum(variables,variable,[-1]*len(variables)))
#                model_blocks.append(Gain(v1,variable,-1))
                
#        print(model_blocks)
        return DynamicSystem(self.te,self.ns,model_blocks)
        
    def _get_ds(self):
        if not self._utd_ds:
            self._dynamic_system=self.GenerateDynamicSystem()
            self._utd_ds=True
        return self._dynamic_system    

    dynamic_system=property(_get_ds)       
        
    def Simulate(self):
        self.dynamic_system.Simulate()
                