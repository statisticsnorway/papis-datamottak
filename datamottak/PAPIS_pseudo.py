# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 14:34:56 2021

@author: oeh
"""

#import pandas as pd
import pyffx
#import time
#import string


def performPseudo(df, varlist, pseudoKey = 'psaudo_'):
    #varAlpha = getAlphabet(df,varlist)
    #print(varAlpha)
    #pseudoFunctions = _createPseudoFunc(varAlpha)  
    #t = time.time()
    
    pseudo = FixedAlphabet(b'secret-key')
    for var in varlist:
        df[str(pseudoKey + var)] = df.apply(
            lambda x: pseudo.encrypt(x[var]), axis=1)
    #for var in varlist:
    #    df[str('pseudo_' + var)] = df.apply(
    #        lambda x: _encrypt(x[var], var, pseudoFunctions, pseudoKey), axis=1)

    #print ("time: {}s".format(time.time()-t))


def _createPseudoFunc(variablesDir):
        retval = {}
        for var, vardir in variablesDir.items():
            retval[var] = {}
            for counter in range(vardir['min'], vardir['max'] + 1):
                retval[var][counter] = pyffx.String(b'secret-key', 
                    alphabet=variablesDir[var]['alphabet'], length=counter)
        return retval
    
    
def _encrypt(val, var, pseudoFunctions, pseudoKey):
    clearText = str(val)
    if len(clearText) > 0:
        func = pseudoFunctions[var][len(clearText)]
        return func.encrypt(clearText)
    else:
        return clearText
"""   
def _encryptRow(self, row, variables, pseudoFunctions, pseudoKey, delOriginal):
        for var in variables:
            clearText = row[var]
            if len(clearText) > 0:
                func = pseudoFunctions[var][len(clearText)]
                row[str(pseudoKey + var)] = func.encrypt(clearText)
            else:
                row[str(pseudoKey + var)] = clearText
            if delOriginal:
                del row[var]
        return row
"""    
    
def getAlphabet(df, varlist, ignore = []):
        retval = _commonIterator(df, varlist, ignore, _iterateAlphabet)
        for el in varlist:
            retval[el]['alphabet'] = _compressAlphabet(retval[el]['alphabet'])
        return retval
    
def _compressAlphabet(varAlphabet):
        temp = sorted(varAlphabet)
        ret = ''
        for char in temp:
            ret += char
        return ret
    
def _commonIterator(df, varlist, ignore, function):
    retval = {}
    if isinstance(varlist, str):
        varlist = [varlist]
    if isinstance(ignore, str):
        ignore = [ignore]
    for el in varlist:
        retval[el] = {}
    #if self_verbose:
    t = time.time()
    line_count = 0
    for elem in varlist:
        line_count += 0
        df.apply(lambda x: function(x[elem], retval[elem], ignore), axis=1)
        #for v in df[elem]:
        #    function(v,)
       # if self._verbose:
    print ("line count: {}".format(line_count))
    print ("time: {}s".format(time.time()-t))
    return retval
    
def _iterateAlphabet(df_el, retval_el, ignore):
        if retval_el.get('alphabet') == None:
            retval_el['alphabet'] = set()
        if df_el in ignore:
            return
        distance = len(str(df_el))
        if(distance == 0):
            retval_el['null'] = retval_el.get('null', 0) + 1
        else:
            if (distance < retval_el.get('min', 100000)):
                retval_el['min'] = distance
            if (distance > retval_el.get('max', 0)):
                retval_el['max'] = distance
            #retval[el][distance] = retval[el].get(distance, 0) + 1
            for char in str(df_el):
                retval_el['alphabet'].add(char)
		
def del_column(df, varlist):
	for var in varlist:
		del df[var]
