from threading import Thread
from time import sleep
import hashlib
from tempfile import TemporaryFile
import io
from papis_service.common.configureServerEnv import ConfigureServerEnv

from datamottak.sas.pseudoSas7bdat import PseudoSas7bdat

class PseudoService(Thread):
    def __init__(self, pseudoDBlocation, pseudoDict, serviceName,
                 app_instance_path, *args, **kwargs ):
        super().__init__()
        
        self.setup = (pseudoDBlocation, pseudoDict, serviceName, app_instance_path) 
        self.name += ' ' + str(serviceName)
        self.worklist = list()
        self.running = False
        self.error = list()
        
    def run(self):
        pseudoDBlocation, pseudoDict, serviceName, app_instance_path = self.setup
        dbService = ConfigureServerEnv.configureDatabase(pseudoDBlocation, app_instance_path)
        pseudoSingleEnv = ConfigureServerEnv.configureSingleEnv(
            serviceName, pseudoDict, dbService)   
        self.pseudoEnv = pseudoSingleEnv
        self.pseudoCache = pseudoSingleEnv.cache
        
        self.running = True
        while self.running:
            if len(self.worklist) == 0:
                sleep(0.5)
            else:
                working_object = self.worklist.pop(0)
                print(f'Working on {working_object}')
                oldFileName, newFileName, pseudoCol, filtype, sftp = working_object
                self.runPseudo(oldFileName, newFileName, pseudoCol, filtype, sftp)
                
    
    def shutdown(self):
        self.running = False
    
    def add(self, jsonfile, sftp):
        workobject = (jsonfile['gammelfil'], jsonfile['nyfil'],
                      jsonfile['pseudoCol'], jsonfile['filetype'], 
                      sftp)
        self.worklist.append(workobject)
    
    def md5(self, filehandle):
        hash_md5 = hashlib.md5()
        tell = filehandle.tell()
        filehandle.seek(0)
        for chunk in iter(lambda: filehandle.read(io.DEFAULT_BUFFER_SIZE), b""):
            hash_md5.update(chunk)
        filehandle.seek(tell)
        return hash_md5.hexdigest()

    def showList(self):
        #Returns a list of objects to undergo pseudonymisation
        return [(x[0], x[1], x[2], x[3]) for x in self.worklist]
        
    def runPseudo(self, oldFileName, newFileName, pseudoCol, filtype, sftp):

        try:
            tempLocalOld = TemporaryFile(mode='w+b', buffering=io.DEFAULT_BUFFER_SIZE)
            sftp.getfo(oldFileName, tempLocalOld)
            md5 = self.md5(tempLocalOld)
            
            tempLocalNew = TemporaryFile(mode='w+b', buffering=io.DEFAULT_BUFFER_SIZE)
            psSasOld = PseudoSas7bdat(fh = tempLocalOld)
            psSasOld.pseudo(pseudoCol, self.pseudoCache, tempLocalNew, encrypt=True)
            
            tempLocalVerify = TemporaryFile(mode='w+b', buffering=io.DEFAULT_BUFFER_SIZE)
            psSasNew = PseudoSas7bdat(fh = tempLocalNew)
            psSasNew.pseudo(pseudoCol, self.pseudoCache, tempLocalVerify, encrypt=False)
            
            md5Verify = self.md5(tempLocalVerify)
            if md5 != md5Verify:
                raise ValueError(f'md5 does not match for file {oldFileName}')
            else:
                print (f'File verified {oldFileName}')
                sftp.putfo(tempLocalNew, newFileName)
            
        except Exception as ex:
            self.error.append((oldFileName, ex))
        finally:
            pass

        