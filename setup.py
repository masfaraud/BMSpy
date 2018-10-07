# -*- coding: utf-8 -*-
"""
Setup install script for BMS

"""

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='bms',
      use_scm_version = True,
      setup_requires = ['setuptools_scm'],
      description = 'Block-Model Simulator for python',
      long_description = readme(),
      keywords = 'block model simulation simulator time',
      url = 'http://github.com/masfaraud/BMSpy/wiki/',
      author = 'Steven Masfaraud',
      author_email = 'steven@masfaraud.fr',
      license = 'Creative Commons Attribution-Share Alike license',
      packages = ['bms', 'bms.blocks', 'bms.signals', 'bms.physical'],
      package_dir = {'bms': 'bms'},
      install_requires = ['numpy', 'matplotlib>=2.0', 'networkx>=2.0', 'dill'],
      classifiers = ['Topic :: Scientific/Engineering', 'Development Status :: 3 - Alpha'])
