# -*- coding: utf-8 -*-
"""
Setup install script for BMS

"""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

def version_scheme(version):
    return '.'.join([str(i) for i in version.tag._key[1]])

def local_scheme(version):
    return ''


setup(name='bms',
      use_scm_version={'version_scheme':version_scheme,'local_scheme':local_scheme},
      setup_requires=['setuptools_scm'],
      description='Block-Model Simulator for python',
      long_description=readme(),
      keywords='block model simulation simulator time',
      url='http://github.com/masfaraud/BMSpy/wiki/',
      author='Steven Masfaraud',
      author_email='steven@masfaraud.fr',
      license='Creative Commons Attribution-Share Alike license',
      packages=['bms','bms.blocks','bms.signals'],
      package_dir={'bms':'bms'},
      install_requires=['numpy','matplotlib>=2.0','networkx','dill'],
      classifiers=['Topic :: Scientific/Engineering','Development Status :: 3 - Alpha'])
