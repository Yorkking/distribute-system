from __future__ import print_function

import random
import logging
import grpc

import file_pb2
import file_pb2_grpc
import os

class FileClient(object):

    def __init__(self,channel,ROOT_PATH='./'):
        self.ROOT_PATH = ROOT_PATH
        self.file_server_stub = file_pb2_grpc.FileStub(channel)
    
    def delete(self,file_name):

        return self.file_server_stub.delete(file_pb2.file(filename=file_name)).isOK
    def upload(self,file_name,s):
        '''
        local_file_name = os.path.join(self.ROOT_PATH,file_name)
        with open(local_file_name,'r',encoding='utf-8')as f:
            s = f.read()
        
            fileInfo = file_pb2.FileInfo(filename=file_name,context=s)
            return self.file_server_stub.upload(fileInfo).isOK
        '''
        fileInfo = file_pb2.FileInfo(filename=file_name,context=s)
        return self.file_server_stub.upload(fileInfo).isOK

    def read(self,file_name):
        result = self.file_server_stub.download(file_pb2.file(filename=file_name))
        context = result.context
        return context
    def download(self,file_name):

        result = self.file_server_stub.download(file_pb2.file(filename=file_name))
        context = result.context
        file = result.filename
        file = os.path.join(self.ROOT_PATH,file)
        if(context):
            with open(file,'w',encoding='utf-8')as f:
                f.write(context)
            return True
        else:
            return False



if __name__ == '__main__':
    file_server_IP = '127.0.0.1'
    file_server_port = '50052'

    with grpc.insecure_channel(str(file_server_IP)+':'+str(file_server_port))as channel:
        
        #file_server_stub = file_pb2_grpc.FileStub(channel)
        print('connected!')
        test = FileClient(channel,'./test/')
        print(test.upload('hello_world.txt'))
        print(test.upload('test.txt'))
        print(test.download('hello_world.txt'))
        #print(test.delete('hello_world.txt'))





