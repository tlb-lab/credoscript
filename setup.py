#!/usr/bin/env python

from distutils.core import setup

setup(name='credoscript',
      version='2012.6.2',
      description='API for the CREDO database',
      author='Adrian Schreyer',
      author_email='ams214@cam.ac.uk',
      license="MIT License",
      url='www-cryst.bioc.cam.ac.uk/credo',
      packages=['credoscript','credoscript.adaptors','credoscript.models',
                'credoscript.mixins','credoscript.contrib','credoscript.ext',
                'credoscript.util','credoscript.support'],
      package_data={'credoscript': ['*.json']},
     )