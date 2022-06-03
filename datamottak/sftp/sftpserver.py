
import time
import socket
import threading

import paramiko

from .stub_sftp import StubServer, StubSFTPServer

def client_start(host = 'localhost', port = 5222,
                 timeout = 60,
                 username = 'test', password = 'test'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port = port, timeout = timeout, 
                username = username, password = password)
    sftp = ssh.open_sftp()
    sftp.chdir('/')
    #sftp.listdir()
    return ssh, sftp

def stop_server():
    for th in threading.enumerate():
        if hasattr(th, 'active'):
            th.active = False

def start_server(host = 'localhost', 
                 port = 5222,
                 timeout = 10,
                 keyfile = r'C:\Users\tir\Desktop\python\rsa_private_test_key.pem',
                 level = 'INFO',
                 BACKLOG = 5):
        thread = threading.Thread(target=_start_server, 
                                  args =(host, port, timeout, keyfile, level, BACKLOG),
                                  name = 'ssh listner')
        thread.start()
    
    
    
def _start_server(host, port, timeout, keyfile,
                  level, BACKLOG):    
    paramiko_level = getattr(paramiko.common, level)
    paramiko.common.logging.basicConfig(level=paramiko_level)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server_socket.settimeout(timeout)
    print(f'FTP Server listening on: {host}:{port} with timeout {timeout}')
    server_socket.bind((host, port))
    server_socket.listen(BACKLOG)
    threading.current_thread().active = True
    cur = threading.current_thread()
    i = 0

    while cur.active == True:
        i = i + 1
        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            #if i < 6:
                #print ("Timeout server")
            continue
        print(f'server connection attempt: {conn}:{port}')
            
        host_key = paramiko.RSAKey.from_private_key_file(keyfile)
        transport = paramiko.Transport(conn)
        transport.add_server_key(host_key)
        transport.set_subsystem_handler(
            'sftp', paramiko.SFTPServer, StubSFTPServer)

        server = StubServer()
        transport.start_server(server=server)

        channel = transport.accept()
        while transport.is_active() and cur.active == True:
            #i = i + 1
            #if i < 6:
            #    print(f'server active {i}')
            time.sleep(5)
            
    print("SERVER stopped")

