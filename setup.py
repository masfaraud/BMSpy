# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 13:14:53 2015

@author: steven
"""

from setuptools import setup

setup(name='bms',
      version='0.0',
      description='Block-Model Simulator for python',
      url='http://github.com/masfaraud/BMSpy',
      author='Steven Masfaraud',
      author_email='steven@masfaraud.fr',
      license='Public Domain',
      packages=['bms'],
      install_requires=['numpy','matplotlib','networkx'],
      zip_safe=False)