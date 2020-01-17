#coding:utf-8
from __future__ import print_function

import random
import logging
import grpc

import directory_pb2_grpc
import directory_pb2

class DirectoryClient(object):

    def __init__(self,channel):
        self.directory_server_stub = directory_pb2_grpc.DirectoryStub(channel)

    def get_file_address(self,file_name):
        temp = directory_pb2.File(filename=file_name)
        temp = self.directory_server_stub.get_file_address(temp)
       
        return (temp.file,temp.client_ip.IP,temp.client_ip.port,temp.timestamp,temp.hostID)

    
    def add_file_address(self,file_name,ip,port,timestamp):
        FileInfo = directory_pb2.AddFileInfo()
        FileInfo.filename = file_name
        FileInfo.ip = ip
        FileInfo.port = port
        FileInfo.timestamp = timestamp
        temp = self.directory_server_stub.add_file_address(FileInfo)
        return temp.isOK
    

    def del_file_address(self,file_name,timestamp):
        temp = directory_pb2.FileSimpleInfo(filename=file_name,timestamp=timestamp)
        result = self.directory_server_stub.del_file_address(temp)
        return result.isOK
    def get_file_all_address(self,file_name):
        '''返回一个ip,port列表
        '''
        temp = directory_pb2.File(filename=file_name)
        result = self.directory_server_stub.get_file_all_address(temp)
        ans = []
        for x in result:
            ans.append( (x.client_ip.IP,x.client_ip.port) )
        return ans

    def get_all_file(self):
        temp = directory_pb2.File(filename='')
        result = self.directory_server_stub.get_all_file(temp)
        ans = [(x.file,x.timestamp,x.hostID) for x in result]
        return ans

    def get_all_server(self):
        temp = directory_pb2.File(filename='')
        result = self.directory_server_stub.get_all_server(temp)
        ans = []
        for x in result:
            ans.append((x.IP,x.port))
        return ans