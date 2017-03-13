Development
===========

BMS is beeing actively developed! Feel free to interact!

Questions and bugs can be reported on github: https://github.com/masfaraud/BMSpy/issues

Release Notes
-------------

see also releases on github: https://github.com/masfaraud/BMSpy/releases


Version 0.0
^^^^^^^^^^^

This is the alpha version. Code standards change rapidely, and compatibility is  this version is not guarentied.

Version 0.0.8
~~~~~~~~~~~~~


 * Physical modeling in order to generate automaticaly dynamic systems from physical components layout.

 * Solver major improvement: loops in dynamic system are solved as a system of equations with an optimizer.


Version 0.0.7
~~~~~~~~~~~~~
Minor changes

Version 0.0.6
~~~~~~~~~~~~~
* Sphinx Documentation
* Variables accessible at time value by DynamicSystem method

Version 0.0.5
~~~~~~~~~~~~~

* Version number standard change
* Model Saving/Loading from file
* New version of model drawing
* Inputs renamed Signals
* Drag & Drop Model drawer

Version 0.04
~~~~~~~~~~~~

* Reorganisation into subpackages of blocks and inputs

Version 0.03
~~~~~~~~~~~~

* Bug correction for float time step
* Redefinition of number of steps

Version 0.02
~~~~~~~~~~~~

* New blocks such as saturation or coulomb
* Bug fixes

Version 0.01
~~~~~~~~~~~~

Initial release



Roadmap
-------

* Implement computation of derivatives at t=0 for inputs
* Implement indicator of convergence when solving at a time step
* Nice model drawing (upgrade existing drag & drop interface)
