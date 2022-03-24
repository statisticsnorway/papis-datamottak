# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 08:46:06 2021

@author: oeh
"""

class FuncInvalidConfigError(Exception):
    """ Raised if a function encounters invalid config """
    pass

class FuncError(Exception):
    """ Raised if an error is is encountered """
    pass

class FileInvalidConfigError(Exception):
    """ Raised if a file encounters invalid config """
    pass

class ArgvInvalidConfigError(Exception):
    """ Raised if argv(json-file) not given """
    pass




