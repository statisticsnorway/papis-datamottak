# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 14:34:56 2021

@author: oeh
"""

#import pandas as pd
from pyffx import FixedAlphabet
#import string


def performPseudo(df, varlist, pseudoKey = 'pseudo_'):
    #varAlpha = getAlphabet(df,varlist)
    #print(varAlpha)
    #pseudoFunctions = _createPseudoFunc(varAlpha)  
    
    pseudo = FixedAlphabet(b'secret-key')
    for var in varlist:
        df[str(pseudoKey + var)] = df.apply(
            lambda x: pseudo.encrypt(x[var]), axis=1)
    #for var in varlist:
    #    df[str('pseudo_' + var)] = df.apply(
    #        lambda x: _encrypt(x[var], var, pseudoFunctions, pseudoKey), axis=1)


def del_column(df, varlist):
	for var in varlist:
		del df[var]
