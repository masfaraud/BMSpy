# -*- coding: utf-8 -*-
"""

"""

from bms import PhysicalNode,PhysicalBlock,Variable,np

class ElectricalNode(PhysicalNode):
    def __init__(self,name=''):
        PhysicalNode.__init__(self,name)
#        self.voltage=Variable(name)
        
class Resistor(PhysicalBlock):
    def __init__(self,node1,node2,R):
        PhysicalBlock.__init__(self,[node1,node2])
        self.R=R
        self.occurence_matrix=np.array([[1,1,1,1],[0,1,0,1]])

class Generator(PhysicalBlock):
    def __init__(self,node1,node2,U):
        PhysicalBlock.__init__(self,[node1,node2])
        self.U=U
        self.occurence_matrix=np.array([[1,0,1,0]])
        
      
class GeneratorGround(PhysicalBlock):
    def __init__(self,node1,node2,U):
        PhysicalBlock.__init__(self,[node1,node2])
        self.U=U
        self.occurence_matrix=np.array([[1,0,0,0],[0,0,1,0]])
        
