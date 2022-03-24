# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 16:16:32 2021

@author: oeh
"""

""" PAPIS-prosjektet - Pseudonymisering av sensitive personopplysninger """

__version__='0.0.1'
__author__= 'Olaf Espeland Hansen'
__all__ = []


from .funksjoner import Funksjoner 
from .logger import loggFile
from .read_json import jsonHandler
from .readers import Reader
from .sas_operasjoner import SAS_Operasjoner
from .pseudo import Pseudo


