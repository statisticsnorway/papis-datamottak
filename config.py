# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 15:08:35 2021

@author: oeh
"""

'''
Global arguments
'''
import os 

# maximum filesize in megabytes
file_mb_max = 100
# encryption key
app_key = 'key'
# full path destination for our upload files
upload_dest = os.path.join(os.getcwd(), 'testfiler')
print(upload_dest)
# list of allowed allowed extensions
extensions = set(['txt','jpg'])