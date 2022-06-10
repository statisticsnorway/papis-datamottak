#!/usr/bin/env python
import logging
import socket
from paramiko.ssh_exception import SSHException
from .stub_sftp import StubServer, StubSFTPServer
import threading
import time

import paramiko

logging.basicConfig()
logger = logging.getLogger()

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        print(f'Check_channel_request: {kind}, {chanid}')
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        else:
            print (f'Check_channel_request failed: {kind}')
            return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
        
    def check_auth_password(self, username, password):
        print('Password ok')
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        #return 'publickey'
        return 'publickey,password'

    def check_channel_exec_request(self, channel, command):
        # This is the command we need to parse
        print (f'Recived command: {command}')
        #self.event.set()
        return True

class SFTPSetup():
    def __init__(self, 
                 keyfile = r'C:\Users\tir\Desktop\python\rsa_private_test_key.pem',
                 listenNum = 10):
        self.keyfile = keyfile
        self.listenNum = listenNum
        
    def sftp_server(self, host = 'localhost', port = 5222,  
                     timeout = 30,
                     level = 'INFO'):
        thread = threading.Thread(target=self._sftp_server, 
                                  args =(host, port, timeout, level),
                                  name = 'sftp listner')
        thread.start()
    
    def _sftp_server(self, host , port, timeout, level):
        paramiko_level = getattr(paramiko.common, level)
        paramiko.common.logging.basicConfig(level=paramiko_level)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        server_socket.settimeout(30)
        server_socket.bind((host, port))
        server_socket.listen(self.listenNum)
        print (f'Start_server: {host},{port}')
        i = 0
        while i<2:
            i += 1
            conn, addr = server_socket.accept()
            print('Socket accepted: {conn, addr}')
            return
            host_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
            transport = paramiko.Transport(conn)
            transport.add_server_key(host_key)
            transport.set_subsystem_handler(
                'sftp', paramiko.SFTPServer, StubSFTPServer)
    
            server = StubServer()
            transport.start_server(server=server)
    
            #channel = transport.accept()
            while transport.is_active():
               print('in loop')
               time.sleep(1)
            print('exit loop')

    def sftp_client(self, host = 'localhost', port = 5222, usern = "test", pw = "test"):
        try:
            transport = paramiko.Transport((host, port))
            transport.connect(username = usern, password = pw)
            print("sftp connecting")
            sftp = paramiko.SFTPClient.from_transport(transport)
            return sftp
        except SSHException as excp:
            #print(f'Exception sftp: {excp}')
            return None
            
        
    def ssh_client(self, port = 5222):
        try:
            ssh = paramiko.SSHClient()
            #ssh.set_log_channel("paramiko")
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('localhost', port = port, username = "test", password = "test")
            #ssh.connect('localhost', port = 5222, username='test', password='test')
            return ssh
        except SSHException as excp:
            print(f'Exception caller: {excp}')

    def ssh_server(self, host = 'localhost', port = 5222, 
                 timeout = 30, level='INFO', stopHafway = False):
        
        paramiko_level = getattr(paramiko.common, level)
        paramiko.common.logging.basicConfig(level=paramiko_level)
        
        thread = threading.Thread(target=self._ssh_server, 
                                  args =(host, port, timeout, stopHafway),
                                  name = 'ssh listner')
        thread.start()
    
    def _ssh_server(self, host, port, timeout, stopHafway):
        print('listener')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        sock.bind((host, port))
        sock.listen(self.listenNum)
        print('set up socket')
        client, addr = sock.accept()
        print(f'socket on {client}:{addr}')
        if stopHafway:
            return



        t = paramiko.Transport(client)
        t.set_gss_host(socket.getfqdn(""))
        t.load_server_moduli()
        host_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        t.add_server_key(host_key)
        server = Server()
        print('paramiko setup')
        t.start_server(server=server)

        print('paramiko running server')
    
        # Wait 30 seconds for a command
        server.event.wait(30)
        print('paramiko waiting...')
        t.close()
        print('paramiko server closed')
    
    # def run_server(self, integer):
    #     try:
    #         if integer == 1:
    #             return self.listener1()
    #         elif integer == 2:
    #             client, addr = self.listener1()
    #             self.listener2(client, addr)
    #     except KeyboardInterrupt:
    #         print('Stopped by keyboardInterrupt')
    #     except Exception as exc:
    #         print(f'Stopped by: {exc}')
    
    def isOpen(self, host = 'localhost', port=5222):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            s.shutdown(2)
            return True
        except:
            return False
            
    
#while True:
#    try:
#        listener()
#    except KeyboardInterrupt:
#        sys.exit(0)
#    except Exception as exc:
#        logger.error(exc)