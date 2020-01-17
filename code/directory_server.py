#coding:utf-8
from concurrent import futures
import time
import math
import logging
import grpc
import directory_pb2
import directory_pb2_grpc
import random
import os
## 路径服务器

class DirectoryServer(directory_pb2_grpc.DirectoryServicer):

    def __init__(self,server_list=None):
        try:
            with open('./logs/directory_server.log','r',encoding='utf-8')as f:
                (self.SEVER_LIST,self.FILE_SERVER,self.FILE_ADDRESS) = eval(f.read())
        except:
            #self.NUM = len(server_list)
            self.SEVER_LIST = [x for x in server_list]
            self.FILE_SERVER = {} # 服务器列表，表示那些活着的服务器，{(ip,port):0,(ip,port):1}
            for index,(ip,port) in enumerate(server_list):
                self.FILE_SERVER[(ip,port)] = index
            self.FILE_ADDRESS = {} # 列表，保存文件的信息，{file_name:[(0,timestamp,hostid),(1,timestamp,hostid)]}
        

    def get_file_address(self, request, context):
        """获取文件的IP,port;随机选取一个文件服务器的IP,port
        """
        file_name = request.filename
        temp = directory_pb2.FileInfo()

        if file_name not in self.FILE_ADDRESS:
            temp.file = ''
            temp.client_ip.IP = ''
            temp.client_ip.port = ''
            temp.timestamp = 0.0
            temp.hostID = ''
        else:
            index0 = random.randint(0,len(self.FILE_ADDRESS[file_name])-1)

            print(self.FILE_ADDRESS)

            server_index,timestamp,host_id = self.FILE_ADDRESS[file_name][index0]
            temp.file = file_name
            temp.client_ip.IP = self.SEVER_LIST[server_index][0]
            temp.client_ip.port = self.SEVER_LIST[server_index][1]
            temp.timestamp = timestamp
            temp.hostID = host_id
        return temp


    def add_file_address(self, request, context):
        pass

        """添加文件所在的路径
            随机选取一个服务器，作为添加的的对象，然后返回该服务器的地址
            然后在客户端，把该更新的消息备份到其余的备份节点时，再把其他服务器的地址添加到该表项
        """
        file_name = request.filename
        timestamp = request.timestamp
        ip = request.ip
        port = request.port

        temp = context.peer().split(':')
        host_id = (temp[1])+':' + (temp[2])

        if file_name in self.FILE_ADDRESS:
            self.FILE_ADDRESS[file_name].append((self.FILE_SERVER[(ip,port)],timestamp,host_id))
        else:
            self.FILE_ADDRESS[file_name] = [(self.FILE_SERVER[(ip,port)],timestamp,host_id)]
        result = True
        self.save_log()
        return directory_pb2.Bool(isOK=result)

    def del_file_address(self, request, context):
        """删除文件所在的路径
        """
        file_name = request.filename
        timestamp = request.timestamp
    
        if file_name not in self.FILE_ADDRESS:
            result = False
        else:
            del self.FILE_ADDRESS[file_name]
            result = True
        self.save_log()
        return directory_pb2.Bool(isOK=result)

    def get_file_all_address(self, request, context):
        """获取存取该文件的所有 file服务器的信息
        """
        file_name = request.filename
        for server_index,timestamp,host_id in self.FILE_ADDRESS[file_name]:
            temp = directory_pb2.FileInfo()
            temp.file = file_name
            temp.client_ip.IP = self.SEVER_LIST[server_index][0]
            temp.client_ip.port = self.SEVER_LIST[server_index][1]
            temp.timestamp = timestamp
            temp.hostID = host_id

            yield temp
    
    def get_all_file(self, request, context):
        """获取所有的文件信息
        """
        temp = directory_pb2.FileInfo()
        for file_name,v_list in self.FILE_ADDRESS.items():
            temp.file = file_name

            ## 这两个信息不重要
            temp.client_ip.IP = ''
            temp.client_ip.port = ''

            temp.timestamp = v_list[0][1] 
            temp.hostID = v_list[0][2] 

            yield temp
    def get_all_server(self, request, context):
        '''
        获取所有服务器的ip，port
        '''
        temp = directory_pb2.ClientIP()

        for (ip,port) in self.SEVER_LIST:
            temp.IP = ip
            temp.port = port

            yield temp
    def save_log(self):
        try:
            os.mkdir('./logs/')
        except:
            pass
        with open('./logs/directory_server.log','w',encoding='utf-8')as f:
            f.write(str((self.SEVER_LIST,self.FILE_SERVER,self.FILE_ADDRESS)))

def run():
    server_list = [('127.0.0.1','50057'),('127.0.0.1','50058'),('127.0.0.1','50059')]
    directory_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    directory_pb2_grpc.add_DirectoryServicer_to_server(
        DirectoryServer(server_list),directory_server
    )
    directory_server.add_insecure_port('127.0.0.1:50052')
    directory_server.start()
    
    directory_server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    run()


