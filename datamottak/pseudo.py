# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 14:34:56 2021

@author: oeh
"""

from papis_pyffx import FixedAlphabet


class Pseudo:

  def __init__(self, pseudoKey = 'pseudo_'):
    self.pseudoKey = pseudoKey

  def performPseudo(self, df, varlist):  
    self.pseudo = FixedAlphabet(b'secret-key')
    for self.var in varlist:
      df[str(self.pseudoKey + self.var)] = df.apply(
            lambda x: self.pseudo.encrypt(x[self.var]), axis=1)

  def _createPseudoFunc(self, variablesDir):
    self.retval = {}
    for self.var, self.vardir in variablesDir.items():
      self.retval[self.var] = {}
      for self.counter in range(self.vardir['min'], self.vardir['max'] + 1):
        self.retval[self.var][self.counter] = pyffx.String(b'secret-key',  
                                              alphabet=variablesDir[self.var]['alphabet'], length=self.counter)
    return self.retval
    
    
  def _encrypt(self, val, var, pseudoFunctions):
    self.clearText = str(val)
    if len(self.clearText) > 0:
      self.func = self.pseudoFunctions[self.var][len(self.clearText)]
      return self.func.encrypt(self.clearText)
    else:
      return self.clearText
    

  def getAlphabet(self, df, varlist, ignore = []):
    self.retval = _commonIterator(df, varlist, ignore, self._iterateAlphabet)
    for self.el in varlist:
      self.retval[self.el]['alphabet'] = self._compressAlphabet(self.retval[self.el]['alphabet'])
    return self.retval
    

  def _compressAlphabet(self, varAlphabet):
    self.temp = sorted(varAlphabet)
    self.ret = ''
    for self.char in self.temp:
       self.ret += self.char
    return self.ret
    
  def _commonIterator(self, df, varlist, ignore, function):
    self.retval = {}
    if isinstance(varlist, str):
      varlist = [varlist]
    if isinstance(ignore, str):
      ignore = [ignore]
    for self.el in varlist:
      self.retval[self.el] = {}
    #if self_verbose:
    self.t = time.time()
    self.line_count = 0
    for self.elem in varlist:
      self.line_count += 0
      df.apply(lambda x: function(x[elem], self.retval[elem], ignore), axis=1)
    print ("line count: {}".format(self.line_count))
    print ("time: {}s".format(time.time()-self.t))
    return self.retval
    

  def _iterateAlphabet(self, df_el, retval_el, ignore):
    if retval_el.get('alphabet') == None:
      retval_el['alphabet'] = set()
    
    if df_el in ignore:
      return
    
    self.distance = len(str(df_el))
    if(self.distance == 0):
      retval_el['null'] = retval_el.get('null', 0) + 1
    else:
      if (self.distance < retval_el.get('min', 100000)):
        retval_el['min'] = self.distance
      if (self.distance > retval_el.get('max', 0)):
        retval_el['max'] = self.distance
    
    for self.char in str(df_el):
      retval_el['alphabet'].add(self.char)
		

  def del_column(self, df, varlist):
    for self.var in varlist:
      del df[self.var]


