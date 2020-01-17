#coding:utf-8
from concurrent import futures
import time
import math
import logging
import grpc
import file_pb2
import file_pb2_grpc
import os

class FileServer(file_pb2_grpc.FileServicer):

    def __init__(self,ROOT_PATH):

        self.ROOT_PATH = ROOT_PATH

    def create(self, request, context):
        """创建一个文件
        """
        file_name = os.path.join(self.ROOT_PATH,request.filename)
        result = False
        try:
            f = open(file_name,'r')
            f.close()
        except:
            with open(file_name,'w') as f:
                result = True

        finally:
            return file_pb2.Bool(isOK=result)
    def delete(self, request, context):
        """删除一个文件 
        """
        file_name = os.path.join(self.ROOT_PATH,request.filename)
        result = True
        try:
            os.remove(file_name)
        except:
            result = False

        return file_pb2.Bool(isOK=result)

    def upload(self, request, context):
        """上传一个文件,判断是否OK
        """
        file_name = os.path.join(self.ROOT_PATH,request.filename)
        file_context = request.context
        result = False
        try:
            f = open(file_name,'r')
            f.close()
        except:
            with open(file_name,'w',encoding='utf-8')as f:
                f.write(file_context)
                result = True
        return file_pb2.Bool(isOK=result)
    def download(self, request, context):
        """读或下载一个文件,判断是否能读
        """
        file_name = os.path.join(self.ROOT_PATH,request.filename)
        result = file_pb2.FileInfo()
        with open(file_name,'r',encoding='utf-8')as f:
            ans = f.read()
            result.filename = request.filename
            result.context = ans
        return result

def run():
    file_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_pb2_grpc.add_FileServicer_to_server(
        FileServer('./'),file_server
    )
    IP = '127.0.0.1'
    port = '50059'
    file_server.add_insecure_port(IP + ':' + port)
    file_server.start()
    file_server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    run()

            