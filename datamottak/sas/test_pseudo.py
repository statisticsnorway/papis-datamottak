from .pseudoSas7bdat import PseudoSas7bdat as Ps
import os


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

def endToEnd(filename, varList, cleanup=True,
             tempDir = r'C:\Users\tir\Desktop\python\sas7bdat\tmpsas'):
    file = Ps(filename)
    if not file.checkColomnNames(varList):
        file.close()
        return False, 'varList is not found in file', filename
    
    enc = file.pseudo(varList, tempDir=tempDir, encrypt=True)
    file.close()
    if same(filename, enc):
        return False, 'no change to file', filename
        
    file2 = Ps(enc)
    dec = file2.pseudo(varList, tempDir=tempDir, encrypt=False)
    file2.close()
    
    comp = same(filename, dec)
    if cleanup:
        os.remove(enc)
        os.remove(dec)
    if (not cleanup) and comp:
        os.remove(dec)
    if comp:
        #End to end success
        return True, file, enc
    else:
        return False, 'Origial and pseudo/depseudo not equal', enc, dec
    
    
    