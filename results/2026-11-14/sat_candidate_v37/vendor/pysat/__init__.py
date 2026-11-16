#!/usr/bin/env python
#-*- coding:utf-8 -*-
##
## __init__.py
##
##  Created on: Mar 4, 2017
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##


# start delvewheel patch
def _delvewheel_patch_1_13_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_13_2()
del _delvewheel_patch_1_13_2
# end delvewheel patch

# current version
#==============================================================================
VERSION = (1, 9, 'dev', 22)


# PEP440 Format
#==============================================================================
__version__ = '%d.%d.%s%d' % VERSION if len(VERSION) == 4 else \
              '%d.%d.%d' % VERSION


# all submodules
#==============================================================================
__all__ = ['card', 'engines', 'formula', 'integer', 'pb', 'process', 'solvers']
