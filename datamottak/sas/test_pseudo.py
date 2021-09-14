from .pseudoSas7bdat import PseudoSas7bdat as Ps
import difflib

def same(name1, name2): 
  with open(name1, "rb") as one: 
    with open(name2, "rb") as two: 
      chunk = other = True 
      while chunk or other: 
        chunk = one.read(4096) 
        other = two.read(4096) 
        if chunk != other: 
          return False 
      return True 

def endToEnd(filename, varList, tempDir = r'C:\Users\tir\Desktop\python\sas7bdat\tmpsas'):
    file = Ps(filename, tempDir=tempDir, encrypt=True)
    file.cached_page = None
    file.readlines2(varList)
    enc = file.tempFile.name
    file.close()
    
    file2 = Ps(enc, tempDir=tempDir, encrypt=False)
    file2.cached_page = None
    file2.readlines2(varList)
    dec = file2.tempFile.name
    file2.close()
    
    return same(filename, dec)
    
    
    