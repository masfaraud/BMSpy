# -*- coding: utf-8 -*-
"""
Setup install script for BMS

"""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

import bms
setup(name='bms',
      version=bms.__version__,# in bms __init__
      description='Block-Model Simulator for python',
      long_description=readme(),
      keywords='block model simulation simulator time',
      url='http://github.com/masfaraud/BMSpy/wiki/',
      author='Steven Masfaraud',
      author_email='steven@masfaraud.fr',
      license='Creative Commons Attribution-Share Alike license',
      packages=['bms','bms.blocks','bms.signals'],
      package_dir={'bms':'bms'},
      install_requires=['numpy','matplotlib','networkx','dill'],
      classifiers=['Topic :: Scientific/Engineering','Development Status :: 3 - Alpha'])