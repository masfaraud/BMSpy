# -*- coding: utf-8 -*-
"""
Core of BMS. All content of this file is imported by bms, and is therefore in bms

This file defines the base of BMS. 

"""

import numpy as np
#import numpy.random
import matplotlib.pyplot as plt
#import math
import networkx as nx
import dill
from scipy.optimize import fsolve, root, minimize
#import cma


class Variable:
    """ Defines a variable

    :param names: Defines full name and short name.

    If names is a string the two names will be identical 
    otherwise names should be a tuple of strings (full_name,short_name) 
    
    :param hidden: inner variable to hide in plots if true
    """

    def __init__(self, names='variable', initial_values=[0], hidden=False):
        if type(names) == str:
            self.name = names
            self.short_name = names
        else:
            try:
                self.short_name = names[1]
                self.name = names[0]
            except:
                raise TypeError

        self.initial_values = initial_values
        self._values = np.array([])
        self.max_order = 0
        self.hidden = hidden

    def _InitValues(self, ns, ts, max_order):
        self.max_order = max_order
        self._values = self.initial_values[0]*np.ones(ns+max_order+1)
        self._ForwardValues()

    def _ForwardValues(self):
        pass

    def _get_values(self):
        return self._values[self.max_order:]

    values = property(_get_values)


class Signal(Variable):
    """ Abstract class of signal """

    def __init__(self, names):
        if type(names) == str:
            self.name = names
            self.short_name = names
        else:
            try:
                self.short_name = names[1]
                self.name = names[0]
            except:
                raise TypeError
                


        self._values = np.array([])
        self.max_order = 0
        self.hidden = False

    def _InitValues(self, ns, ts, max_order):
        self.max_order = max_order
        self._values = np.zeros(ns+max_order+1)
        for i in range(ns+1):
            self._values[i+max_order] = self.function(i*ts)
        self._ForwardValues()
        self.initial_values = [self._values[0]]


    def _ForwardValues(self):
        """
        Implementation for problems with derivative conditions on variables
        """
        pass


class Block:
    """ Abstract class of block: this class should not be instanciate directly
    """

    def __init__(self, inputs, outputs, max_input_order, max_output_order):
        self.inputs = []
        self.outputs = []

        self.n_inputs = len(inputs)
        self.n_outputs = len(outputs)

        for variable in inputs:
            self._AddInput(variable)
        for variable in outputs:
            self._AddOutput(variable)

#        self.input_orders=
#        self.output_orders=output_orders
        self.max_input_order = max_input_order
        self.max_output_order = max_output_order
        self.max_order = max(self.max_input_order, self.max_output_order)

    def _AddInput(self, variable):
        """
        Add one more variable as an input of the block

        :param variable: variable (or signal as it is also a variable)
        """
        if isinstance(variable, Variable):
            self.inputs.append(variable)
        else:
            print('Error: ', variable.name, variable,
                  ' given is not a variable')
            raise TypeError

    def _AddOutput(self, variable):
        """
            Add one more variable as an output of the block

            :param variable: variable (or signal as it is also a variable)
        """
        if isinstance(variable, Variable):
            self.outputs.append(variable)
        else:
            print(variable)
            raise TypeError

    def InputValues(self, it, nsteps=None):
        """
            Returns the input values at a given iteration for solving the block outputs
        """
        if nsteps == None:
            nsteps = self.max_input_order
#        print(self,it)
        # Provides values in inputs values for computing at iteration it
        I = np.zeros((self.n_inputs, nsteps))
        for iv, variable in enumerate(self.inputs):
            #            print(it-self.max_input_order+1,it+1)
            #            print(variable._values[it-self.max_input_order+1:it+1])
            I[iv, :] = variable._values[it-nsteps+1:it+1]
        return I

    def OutputValues(self, it, nsteps=None):
        # Provides values in inputs values for computing at iteration it
        if nsteps == None:
            nsteps = self.max_output_order
        O = np.zeros((self.n_outputs, nsteps))
        for iv, variable in enumerate(self.outputs):
            O[iv, :] = variable._values[it-nsteps:it]
        return O

    def Solve(self, it, ts):
        self.outputs[0]._values[it] = self.Evaluate(it, ts)


class ModelError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Model Error: '+self.message


class DynamicSystem:
    """
    Defines a dynamic system that can simulate itself

    :param te: time of simulation's end 
    :param ns: number of steps
    :param blocks: (optional) list of blocks defining the model        

    """

    def __init__(self, te, ns, blocks=[]):
        self.te = te
        self.ns = ns
        self.ts = self.te/float(self.ns)  # time step
        self.t = np.linspace(0, self.te, num=ns+1)  # Time vector
        self.blocks = []
        self.variables = []
        self.signals = []

        self.max_order = 0

        for block in blocks:
            self.AddBlock(block)

        self._utd_graph = False  # True if graph is up-to-date

    def AddBlock(self, block):
        """
        Add the given block to the model and also its input/output variables
        """
        if isinstance(block, Block):
            self.blocks.append(block)
            self.max_order = max(self.max_order, block.max_input_order-1)
            self.max_order = max(self.max_order, block.max_output_order)
            for variable in block.inputs+block.outputs:
                self._AddVariable(variable)
        else:
            print(block)
            raise TypeError
        self._utd_graph = False

    def _AddVariable(self, variable):
        """
        Add a variable to the model. Should not be used by end-user
        """
        if isinstance(variable, Signal):
            if not variable in self.signals:
                self.signals.append(variable)
        elif isinstance(variable, Variable):
            if not variable in self.variables:
                self.variables.append(variable)
        else:
            raise TypeError
        self._utd_graph = False

    def _get_Graph(self):
        if not self._utd_graph:
            # Generate graph
            self._graph = nx.DiGraph()
            for variable in self.variables:
                self._graph.add_node(variable, bipartite=0)
            for block in self.blocks:
                self._graph.add_node(block, bipartite=1)
                for variable in block.inputs:
                    self._graph.add_edge(variable, block)
                for variable in block.outputs:
                    self._graph.add_edge(block, variable)

            self._utd_graph = True
        return self._graph

    graph = property(_get_Graph)

    def _ResolutionOrder(self, variables_to_solve):
        """
        return a list of lists of tuples (block,output,ndof) to be solved

        """
#    Gp=nx.DiGraph()
#
#    for i in range(nvar):
#        Gp.add_node('v'+str(i),bipartite=0)
#
#    for i in range(neq):
#        Gp.add_node('e'+str(i),bipartite=1)
#        for j in range(nvar):
#            if Mo[i,j]==1:
#                Gp.add_edge('e'+str(i),'v'+str(j))

        Gp = nx.DiGraph()
        for variable in self.variables:
            Gp.add_node(variable, bipartite=0)
        for block in self.blocks:
            for iov, output_variable in enumerate(block.outputs):
                Gp.add_node((block, iov), bipartite=1)
                Gp.add_edge((block, iov), output_variable)
                Gp.add_edge(output_variable, (block, iov))
                for input_variable in block.inputs:
                    if not isinstance(input_variable, Signal):
                        Gp.add_edge(input_variable, (block, iov))

    #    for n1,n2 in M.items():
    #        Gp.add_edge(n1,n2)

        sinks = []
        sources = []
        for node in Gp.nodes():
            if Gp.out_degree(node) == 0:
                sinks.append(node)
            elif Gp.in_degree(node) == 0:
                sources.append(node)

        G2 = sources[:]
        for node in sources:
            for node2 in nx.descendants(Gp, node):
                if node2 not in G2:
                    G2.append(node2)

        if G2 != []:
            print(G2)
            raise ModelError('Overconstrained variables')

        G3 = sinks[:]
        for node in sinks:
            for node2 in nx.ancestors(Gp, node):
                if node2 not in G3:
                    G3.append(node2)

        if G3 != []:
            raise ModelError('Underconstrained variables')

#        vars_resolvables=[]
#        for var in vars_resoudre:
#            if not 'v'+str(var) in G2+G3:
#                vars_resolvables.append(var)


#        G1=Gp.copy()
#        G1.remove_nodes_from(G2+G3)
#
#        M1=nx.bipartite.maximum_matching(G1)
#        G1p=nx.DiGraph()
#
#        G1p.add_nodes_from(G1.nodes())
#        for e in G1.edges():
#            # equation vers variable
#            if e[0][0]=='v':
#                G1p.add_edge(e[0],e[1])
#            else:
#                G1p.add_edge(e[1],e[0])
#    #    print(len(M))
#        for n1,n2 in M1.items():
#    #        print(n1,n2)
#            if n1[0]=='e':
#                G1p.add_edge(n1,n2)
#            else:
#                G1p.add_edge(n2,n1)

        scc = list(nx.strongly_connected_components(Gp))
    #    pos=nx.spring_layout(G1p)
    #    plt.figure()
    #    nx.draw(G1p,pos)
    #    nx.draw_networkx_labels(G1p,pos)
#        print(scc)
        if scc != []:
            C = nx.condensation(Gp, scc)
            isc_vars = []
            for isc, sc in enumerate(scc):
                for var in variables_to_solve:
                    if var in sc:
                        isc_vars.append(isc)
                        break
            ancestors_vars = isc_vars[:]

            for isc_var in isc_vars:
                for ancetre in nx.ancestors(C, isc_var):
                    if ancetre not in ancestors_vars:
                        ancestors_vars.append(ancetre)

            order_sc = [sc for sc in nx.topological_sort(
                C) if sc in ancestors_vars]
            order_ev = []
            for isc in order_sc:
                # liste d'équations et de variables triées pour être séparées
                evs = list(scc[isc])
#                print(evs)
#                levs=int(len(evs)/2)
                eqs = []
                var = []
                for element in evs:
                    if type(element) == tuple:
                        eqs.append(element)
                    else:
                        var.append(element)
                order_ev.append((len(eqs), eqs, var))

            return order_ev

        raise ModelError

    def Simulate(self, variables_to_solve=None):
        if variables_to_solve == None:
            variables_to_solve = [
                variable for variable in self.variables if not variable.hidden]

        order = self._ResolutionOrder(variables_to_solve)

        # Initialisation of variables values
        for variable in self.variables+self.signals:
            variable._InitValues(self.ns, self.ts, self.max_order)

# ==============================================================================
#         Enhancement to do: defining functions out of loop (copy args)s
# ==============================================================================
#        print(order)
        residue = []
        for it, t in enumerate(self.t[1:]):
            for neqs, equations, variables in order:
                if neqs == 1:
                    equations[0][0].Solve(it+self.max_order+1, self.ts)
                else:
                    #                    x0=np.zeros(neqs)
                    x0 = [equations[i][0].outputs[equations[i][1]]._values[it +
                                                                           self.max_order] for i in range(len(equations))]
#                    print('===========')

                    def r(x, equations=equations[:]):
                        # Writing variables values proposed by optimizer
                        for i, xi in enumerate(x):
                            equations[i][0].outputs[equations[i][1]
                                                    ]._values[it+self.max_order+1] = xi

                        # Computing regrets
                        r = []
#                        s=0
                        for ieq, (block, neq) in enumerate(equations):
                            #                            print(block,it)
                            #                            print(block.Evaluate(it+self.max_order+1,self.ts).shape)
                            #                            print(block.Evaluate(it+self.max_order+1,self.ts),block)
                            r.append(x[ieq]-block.Evaluate(it +
                                                           self.max_order+1, self.ts)[neq])
#                            print(block)
#                            print('xproposed:',x[ieq])
#                            print('block eval',block.Evaluate(it+self.max_order+1,self.ts)[neq])
#                            print('value', x[ieq]-block.Evaluate(it+self.max_order+1,self.ts)[neq])
#                            s+=abs(x[ieq]-block.Evaluate(it+self.max_order+1,self.ts)[neq])
#                            print(x[ieq],block.Evaluate(it+self.max_order+1,self.ts)[neq])
                        return r

                    def f(x, equations=equations[:]):
                        # Writing variables values proposed by optimizer
                        for i, xi in enumerate(x):
                            equations[i][0].outputs[equations[i][1]
                                                    ]._values[it+self.max_order+1] = xi

                        # Computing regrets
#                        r=[]
                        s = 0
                        for ieq, (block, neq) in enumerate(equations):
                            #                            print(block,it)
                            #                            print(block.Evaluate(it+self.max_order+1,self.ts).shape)
                            #                            print(block.Evaluate(it+self.max_order+1,self.ts),block)
                            #                            r.append(x[ieq]-block.Evaluate(it+self.max_order+1,self.ts)[neq])
                            #                            print(block)
                            s += abs(x[ieq]-block.Evaluate(it +
                                                           self.max_order+1, self.ts)[neq])
#                            print(x[ieq],block.Evaluate(it+self.max_order+1,self.ts)[neq])
#                        return r
#                        print(s)
                        return s

                    x, d, i, m = fsolve(r, x0, full_output=True)
#                    res=root(f,x0,method='anderson')
#                    x=res.x


#                    res=minimize(f,x0,method='powell')
#                    if res.fun>1e-3:
#                        x0=[equations[i][0].outputs[equations[i][1]]._values[it+self.max_order] for i in range(len(equations))]
#                        x0+=np.random.random(len(equations))
#                        print('restart')
#                        res=minimize(f,x0,method='powell')
#
#                    residue.append(f(res.x))


#                    print(r(x),i)
#                    print(f(res.x),res.fun)
#                    f(x)
#                    print(r)
#                    if i!=1:
#                        print(equations)
#                        print(i,r(x))
#                        options={'tolfun':1e-3,'verbose':-9,'ftarget':1e-3}
#                        res=cma.fmin(f,x0,1,options=options)
#                        print(f(res[0]),r(res[0]))
# print(equations)
#
# print(m)
# if res.fun>1e-3:
# print('fail',res.fun)
# options={'tolfun':1e-3,'verbose':-9}
# res=cma.fmin(f,x0,1,options=options)
# else:
# print('ok')
#        return residue

    def VariablesValues(self, variables, t):
        """
        Returns the value of given variables at time t. 
        Linear interpolation is performed between two time steps.

        :param variables: one variable or a list of variables
        :param t: time of evaluation
        """
        # TODO: put interpolation in variables
        if (t < self.te) | (t > 0):
            i = t//self.ts  # time step
            ti = self.ts*i
            if type(variables) == list:
                values = []
                for variable in variables:
                    # interpolation
                    values.append(
                        variables.values[i]*((ti-t)/self.ts+1)+variables.values[i+1]*(t-ti)/self.ts)
                return values

            else:
                # interpolation
                return variables.values[i]*((ti-t)/self.ts+1)+variables.values[i+1]*(t-ti)/self.ts
        else:
            raise ValueError

    def PlotVariables(self, subplots_variables=None):
        if subplots_variables == None:
            subplots_variables = [self.signals+self.variables]
            subplots_variables = [
                [variable for variable in self.signals+self.variables if not variable.hidden]]
#        plt.figure()
        fig, axs = plt.subplots(len(subplots_variables), sharex=True)
        if len(subplots_variables) == 1:
            axs = [axs]
        for isub, subplot in enumerate(subplots_variables):
            legend = []
            for variable in subplot:
                axs[isub].plot(self.t, variable.values)
                legend.append(variable.name)
            axs[isub].legend(legend, loc='best')
            axs[isub].margins(0.08)
            axs[isub].grid()

        plt.xlabel('Time')
        plt.show()

    def DrawModel(self):
        from .interface import ModelDrawer
        ModelDrawer(self)

    def Save(self, name_file):
        """
            name_file: name of the file without extension.
            The extension .bms is added by function
        """
        with open(name_file+'.bms', 'wb') as file:
            model = dill.dump(self, file)

    def __getstate__(self):
        dic = self.__dict__.copy()
        return dic

    def __setstate__(self, dic):
        self.__dict__ = dic


def Load(file):
    """ Loads a model from specified file """
    with open(file, 'rb') as file:
        model = dill.load(file)
        return model


class PhysicalNode:
    """
    Abstract class
    """

    def __init__(self, cl_solves_potential, cl_solves_fluxes, node_name, potential_variable_name, flux_variable_name):
        self.cl_solves_potential = cl_solves_potential
        self.cl_solves_fluxes = cl_solves_fluxes
        self.name = node_name
        self.potential_variable_name = potential_variable_name
        self.flux_variable_name = flux_variable_name
        self.variable = Variable(potential_variable_name+' '+node_name)


class PhysicalBlock:
    """
    Abstract class to inherit when coding a physical block
    """

    def __init__(self, physical_nodes, nodes_with_fluxes, occurence_matrix, commands, name):
        self.physical_nodes = physical_nodes
        self.name = name
        self.nodes_with_fluxes = nodes_with_fluxes
        self.occurence_matrix = occurence_matrix
        self.commands = commands
        self.variables = [Variable(physical_nodes[inode].flux_variable_name+' from ' +
                                   physical_nodes[inode].name+' to '+self.name) for inode in nodes_with_fluxes]


class PhysicalSystem:
    """
    Defines a physical system
    """

    def __init__(self, te, ns, physical_blocks, command_blocks):
        self.te = te
        self.ns = ns
        self.physical_blocks = []
        self.physical_nodes = []
        self.variables = []
        self.command_blocks = []
        for block in physical_blocks:
            self.AddPhysicalBlock(block)

        for block in command_blocks:
            self.AddCommandBlock(block)

        self._utd_ds = False

    def AddPhysicalBlock(self, block):
        if isinstance(block, PhysicalBlock):
            self.physical_blocks.append(block)
            for node in block.physical_nodes:
                self._AddPhysicalNode(node)
        else:
            raise TypeError
        self._utd_ds = False

    def _AddPhysicalNode(self, node):
        if isinstance(node, PhysicalNode):
            if not node in self.physical_nodes:
                self.physical_nodes.append(node)
        self._utd_ds = False

    def AddCommandBlock(self, block):
        if isinstance(block, Block):
            self.command_blocks.append(block)
            for variable in block.inputs+block.outputs:
                self._AddVariable(variable)
        else:
            raise TypeError
        self._utd_ds = False

    def _AddVariable(self, variable):
        if isinstance(variable, Variable):
            if not variable in self.variables:
                self.variables.append(variable)
        self._utd_ds = False

    def GenerateDynamicSystem(self):
        #        from bms.blocks.continuous import WeightedSum
        G = nx.Graph()
#        variables={}
        # Adding node variables
        for node in self.physical_nodes:
            G.add_node(node.variable, bipartite=0)
        for block in self.physical_blocks:
            #            print(block.variables)
            for variable in block.variables:
                # add variable realted to connection
                G.add_node(node.variable, bipartite=0)
            ne, nv = block.occurence_matrix.shape
#            print(block,block.occurence_matrix)
            # Add equations of blocs
            for ie in range(ne):
                G.add_node((block, ie), bipartite=1)
                for iv in range(nv):
                    #                    print(iv)
                    if block.occurence_matrix[ie, iv] == 1:
                        if iv % 2 == 0:
                            G.add_edge(
                                (block, ie), block.physical_nodes[iv//2].variable)
                        else:
                            G.add_edge((block, ie), block.variables[iv//2])
        # Adding equation of physical nodes: conservative law of node from its occurence matrix
        # Restricted to nodes to which are brought fluxes
        for node in self.physical_nodes:
            # linking conservative equation of flux to potential if
            if node.cl_solves_potential:
                G.add_edge(node, node.variable)
            if node.cl_solves_fluxes:
                # Linking fluxes of node
                G.add_node(node, bipartite=1)
                for block in self.physical_blocks:
                    for inb in block.nodes_with_fluxes:
                        #                    print(block,block.physical_nodes[inb].name)
                        node_block = block.physical_nodes[inb]
                        if node == node_block:
                            G.add_edge(
                                node, block.variables[block.nodes_with_fluxes.index(inb)])
    #                        print(node_block,block.variables[inb].name)

#        # Draw graph for debug
#        pos=nx.spring_layout(G)
#        nx.draw(G,pos)
#        names={}
#        for node in G.nodes():
#            if type(node)==tuple:
#                names[node]=(node[0].name,node[1])
#            else:
#                names[node]=node.name
#        nx.draw_networkx_labels(G,pos,names)
#        plt.show()

        G2 = nx.DiGraph()
        G2.add_nodes_from(G)
        eq_out_var = {}
        for e in nx.bipartite.maximum_matching(G).items():
            #            print(e[0].__class__.__name__)
            # eq -> variable
            if e[0].__class__.__name__ == 'Variable':
                G2.add_edge(e[1], e[0])
                eq_out_var[e[1]] = e[0]
            else:
                G2.add_edge(e[0], e[1])
                eq_out_var[e[0]] = e[1]

        for e in G.edges():
            if e[0].__class__.__name__ == 'Variable':
                G2.add_edge(e[0], e[1])
            else:
                G2.add_edge(e[1], e[0])
#        print('@@@@@@@@@@@@@@@@@@@@@@@@')

        sinks = []
        sources = []
        for node in G2.nodes():
            if G2.out_degree(node) == 0:
                sinks.append(node)
            elif G2.in_degree(node) == 0:
                sources.append(node)
#        print(sinks,sources)

        if sinks != []:
            print(sinks)
            raise ModelError
        if sources != []:
            print(sources)
            raise ModelError

        # Model is solvable: it must say to equations of blocks which is their
        # output variable

#        print(eq_out_var)
        model_blocks = []
        for block_node, variable in eq_out_var.items():
            #            print(block_node,variable)
            if type(block_node) == tuple:
                # Blocks writes an equation
                model_blocks.extend(
                    block_node[0].PartialDynamicSystem(block_node[1], variable))
            else:
                # Sum of incomming variables at nodes
                # searching attached nodes
                variables = []
                for block in self.physical_blocks:
                    try:
                        ibn = block.physical_nodes.index(block_node)
                        if ibn in block.nodes_with_fluxes:
                            variable2 = block.variables[ibn]
                            if variable2 != variable:
                                variables.append(variable2)
                    except ValueError:
                        pass

#                model_blocks.append(WeightedSum(variables,variable,[-1]*len(variables)))
                model_blocks.extend(
                    block_node.ConservativeLaw(variables, variable))

                #                model_blocks.append(Gain(v1,variable,-1))

        model_blocks.extend(self.command_blocks)
        return DynamicSystem(self.te, self.ns, model_blocks)

    def _get_ds(self):
        if not self._utd_ds:
            self._dynamic_system = self.GenerateDynamicSystem()
            self._utd_ds = True
        return self._dynamic_system

    dynamic_system = property(_get_ds)

    def Simulate(self):
        self.dynamic_system.Simulate()
