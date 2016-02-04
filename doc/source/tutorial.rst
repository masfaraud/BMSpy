Tutorial
========

The DynamicSystem Class is a python class defined by BMS core. It allows to define a complete model containing all the data for simulation.

Defining a model
----------------

.. code:: python
    import bms

Defining the inputs
^^^^^^^^^^^^^^^^^^^

Inputs are special variable in the model which are not computed. See the [inputs list](Inputs)
Here we define a ramp named which name is e

.. code:: python

  e=Ramp('e',1.)

Defining Variables
^^^^^^^^^^^^^^^^^^

Let's define a variable s which will be the output of a first order block

.. code:: python

  s=bms.Variable('s')

Defining Blocks
^^^^^^^^^^^^^^^

Let's define this block:

.. code:: python

   from bms.blocks.continuous import ODE
    block=ODE(e,s,[1],[1,3])

Defining the model
^^^^^^^^^^^^^^^^^^

.. code:: python

    te=10# time of end in seconds
    ns=2000 # number of time steps
    model=bms.DynamicSystem(te,ns,[block])

The blocks are given in a list as third argument

Model methods
-------------


Simulating
^^^^^^^^^^

.. code:: python

    model.Simulate()

Plotting variables
^^^^^^^^^^^^^^^^^^

.. code:: python

    model.PlotVariables()

Accessing values
^^^^^^^^^^^^^^^^

Values of variables at a given time t is accessible by:

.. code:: python

  ds.VariablesValues(t)


The time values vector of a variable is accessible via the values attribute:

.. code:: python

     import matplotlib.pyplot as plt
     plt.plot(ds.t,e.values)
     plt.plot(ds.t,s.values)



Examples
========
See the project examples folder on github: https://github.com/masfaraud/BMSpy/tree/master/bms/examples


