# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 22:48:50 2016

@author: steven
"""

import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
#import matplotlib.cm as cm
import numpy as np
import bms
#import cma
import math
import itertools
import networkx as nx


class ModelDrawer:

    def __init__(self, model):
        """ Create a new drag handler and connect it to the figure's event system.
        If the figure handler is not given, the current figure is used instead
        """
        import matplotlib.pyplot as plt
        self.l = 0.05
#        plt.figure()
        self.dragged = None
        self.model = model
        self.element_from_artist = {}  # patch->block
        self.artists_from_element = {}

        self.noeud_clic = None

        # Initialisation of positions
        # networkx positionning
        self.position = nx.spring_layout(self.model.graph)

#        self.position={}
#        # Random positionning
# for block in self.model.blocks:
# self.position[block]=[random.random(),random.random()]
# for variable in self.model.variables+self.model.signals:
# self.position[variable]=[random.random(),random.random()]
#        # optimized positionning
# lx=# len
#        dof={}
#        # Parametrizing
#        i=0
#        for block in self.model.blocks:
#            dof[block]=[i,i+1]
#            i+=2
#        for variables in self.model.variables+self.model.signals:
#            dof[variables]=[i,i+1]
#            i+=2
#
#        print(len(list(dof.keys())))
#
#        # function definition
#        cp=100000# penalty coefficient
#        dt=self.l*5# target distance between stuff
#        def f(x,verbose=False):
#            if verbose:
#                print('======================')
#            r=0# result
#            for block in self.model.blocks:
#                db=dof[block]
#                # each block must have its inputs at its left
#                for variable in block.inputs:
#                    dv=dof[variable]
#                    xb=x[db]
#                    xv=x[dv]
#                    if xb[0]<xv[0]:
#                        r+=cp*(xv[0]-xb[0])**2
#                    # minimize distance between block and connections
#                    d=math.sqrt((xb[0]-xv[0])**2+(xb[1]-xv[1])**2)
#                    if d>dt:
#                        r+=d-dt
#                        if verbose:
#                           print('dbc: ',d-dt)
#                    # connection must be as horizontal as possible
#                    if verbose:
#                       print('hz: ',abs(xb[1]-xv[1]))
#                    r+=abs(xb[1]-xv[1])
#                # each block must have its outputs at its right
#                for variable in block.outputs:
#                    dv=dof[variable]
#                    xb=x[db]
#                    xv=x[dv]
#                    if xb[0]>xv[0]:
#                        r+=cp*(xb[0]-xv[0])**2
#                        if verbose:
#                            print('output right: ',cp*(xb[0]-xv[0])**2)
#
#                    # minimize distance between block and connections
#                    d=math.sqrt((xb[0]-xv[0])**2+(xb[1]-xv[1])**2)
#                    if d>dt:
#                        r+=d-dt
#                    # connection must be as horizontal as possible
#                    r+=abs(xb[1]-xv[1])
#                    if verbose:
#                        print(abs(xb[1]-xv[1]))
#
#            # Avoid closeness of elements:
#            for e1,e2 in itertools.combinations(self.model.signals+self.model.blocks+self.model.variables,2):
#                xe1=dof[e1]
#                xe2=dof[e2]
#                de12=math.sqrt((xe1[0]-xe2[0])**2+(xe1[1]-xe2[1])**2)
#                if de12<dt:
#                    r+=abs((dt-de12)*cp)
#                    if verbose:
#                        print(abs((dt-de12)*cp))
# print(r)
#            return r
#
#        options={'bounds':[-50*self.l,50*self.l],'ftarget':0}#,'tolfun':1e-4,'ftarget':-ndemuls*(1-0.07),'verbose':-9}
#        res=cma.fmin(f,np.random.random(2*len(list(dof.keys()))),2*dt,options=options)
#        xopt=res[0]
# f_opt=-res[1]
#        print(xopt)
#        f(xopt,True)
#        for element in self.model.signals+self.model.blocks+self.model.variables:
#            de=dof[element]
#            self.position[element]=(xopt[de[0]],xopt[de[1]])

        # Drawing
        plt.ioff()

        self.fig, self.ax = plt.subplots(1, 1)
        for variable in self.model.signals:
            points = np.array((5, 2))
            xp, yp = self.position[variable]
            points = np.array([[xp-1.5*self.l, yp-0.5*self.l], [xp-0.5*self.l, yp-0.5*self.l], [
                              xp, yp], [xp-0.5*self.l, yp+0.5*self.l], [xp-1.5*self.l, yp+0.5*self.l]])
            p = mpatches.Polygon(points, facecolor='white',
                                 edgecolor='black', picker=10)
            self.ax.add_patch(p)
            t = self.ax.text(xp-1*self.l, yp, variable.short_name, color='black',
                             ha='center', multialignment='center', verticalalignment='center')
            self.element_from_artist[p] = variable
            # polygon, text, arrows in, arrows out
            self.artists_from_element[variable] = [p, t, [], []]

        for variable in self.model.variables:
            #            p=mpatches.Circle(self.position[variable],radius=0.025,facecolor='white',edgecolor='black')
            #            p=mpatches.FancyBboxPatch((bb.xmin, bb.ymin),2*l,l,boxstyle="round,pad=0.",ec="k", fc="none", zorder=10.)
            #            self.ax.add_patch(p)
            pos = self.position[variable]
            t = self.ax.text(pos[0], pos[1], variable.short_name, color='black', ha='center', picker=10,
                             multialignment='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
            self.element_from_artist[t] = variable
            # text,arrows in arrows out None stands for standard
            self.artists_from_element[variable] = [t, None, [], []]

        for block in self.model.blocks:
            hb = 0.5*(1+max(len(block.inputs), len(block.outputs)))*self.l
            pb = self.position[block][:]
            p = mpatches.Rectangle((pb[0]-0.5*self.l, pb[1]-hb/2), height=hb,
                                   width=self.l, edgecolor='black', facecolor='#CCCCCC', picker=10)
            self.ax.add_patch(p)
            t = self.ax.text(pb[0], pb[1], block.LabelBlock(
            ), color='black', multialignment='center', verticalalignment='center')
            self.element_from_artist[p] = block
            self.artists_from_element[block] = [p, t]

            # Block connections
            for iv, variable in enumerate(block.inputs):
                pv = self.position[variable]
                pcb = self.position[block][:]  # Position connection on block
                a = mpatches.FancyArrowPatch(
                    pv, (pb[0]-0.5*self.l, pb[1]+hb/2-0.5*(iv+1)*self.l), arrowstyle='-|>')
                self.ax.add_patch(a)
                self.artists_from_element[block].append(a)
                self.artists_from_element[variable][3].append(a)

            for iv, variable in enumerate(block.outputs):
                pv = self.position[variable]
                pb = self.position[block]
                a = mpatches.FancyArrowPatch(
                    (pb[0]+0.5*self.l, pb[1]+hb/2-0.5*(iv+1)*self.l), pv, arrowstyle='-|>')
                self.ax.add_patch(a)
                self.artists_from_element[block].append(a)
                self.artists_from_element[variable][2].append(a)

        plt.axis('equal')
        plt.margins(0.05)

        # Connect events and callbacks
#        self.fig.canvas.mpl_connect("button_release_event", self.on_release_event)
        self.fig.canvas.mpl_connect("pick_event", self.on_pick_event)
        self.fig.canvas.mpl_connect(
            "button_release_event", self.on_release_event)
        plt.show()

    def on_pick_event(self, event):
        #        print(event.artist)
        #        print(self.artists[event.artist])
        self.selected_patch = event.artist

    def on_release_event(self, event):
        " Update text position and redraw"
        element = self.element_from_artist[self.selected_patch]
        self.position[element] = [event.xdata, event.ydata]
        # Signal is a variable! therefore must be tested before
        if isinstance(element, bms.Signal):
            artists = self.artists_from_element[element]
            points = np.array((5, 2))
            xp, yp = self.position[element]
            points = np.array([[xp-1.5*self.l, yp-0.5*self.l], [xp-0.5*self.l, yp-0.5*self.l], [
                              xp, yp], [xp-0.5*self.l, yp+0.5*self.l], [xp-1.5*self.l, yp+0.5*self.l]])
            artists[0].set_xy(xy=points)
            artists[1].set(x=xp-1*self.l, y=yp)
            for artist in artists[3]:  # update out arrows
                artist.set_positions((xp, yp), None)

        elif isinstance(element, bms.Variable):
            artists = self.artists_from_element[element]
            pos = self.position[element]
            artists[0].set(x=pos[0], y=pos[1])
            for artist in artists[2]:  # update in arrows
                artist.set_positions(None, pos)
            for artist in artists[3]:  # update out arrows
                artist.set_positions(pos, None)

        elif isinstance(element, bms.Block):
            artists = self.artists_from_element[element]
            pb = self.position[element][:]
            hb = 0.5*(1+max(len(element.inputs), len(element.outputs)))*self.l
            artists[0].set(xy=(pb[0]-0.5*self.l, pb[1]-hb/2))
            artists[1].set(x=pb[0], y=pb[1])
            li = len(element.inputs)
#            lo=len(element.outputs)
            for i in range(2, li+2):
                artists[i].set_positions(
                    None, (pb[0]-0.5*self.l, pb[1]+hb/2-0.5*(i+1-2)*self.l))
            for i in range(2+li, len(artists)):
                artists[i].set_positions(
                    (pb[0]+0.5*self.l, pb[1]+hb/2-0.5*(i+1-2-li)*self.l), None)

        plt.draw()
        return True
