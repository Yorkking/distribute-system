#coding:utf-8
from concurrent import futures
import time
import math
import logging
import grpc
import lock_pb2
import lock_pb2_grpc


class LockServer(lock_pb2_grpc.LockServicer):
    
    def __init__(self):
        self.LOCK_TIMEOUT = 30

        ## 设置两种锁，分别是共享锁和排他锁
        self.SHARE_LOCK = {} 
        self.EXCLUSIVE_LOCK = {}

    def lock_exist_test(self, request, context):
        """
        判断文件是否加锁
        文件的名字，返回一个锁类型：0无锁，1共享锁，2互斥锁
        """
        file_name = request.filename
        result = 0
        if(file_name in self.EXCLUSIVE_LOCK):
            result = 2
        elif file_name in self.SHARE_LOCK:
            result = 1
        #print("addr: ",type(context.peer()))
        return lock_pb2.TypeLock(typelock=result)

    def get_lock_client(self, request, context):
        """获得加锁的文件的客户端信息
        args: filename
        returns: clientInfo: IP:string,port:string
        """
        file_name = request.filename
        if(file_name in self.EXCLUSIVE_LOCK):
            ip,port,type_lock = self.EXCLUSIVE_LOCK[file_name]
            yield lock_pb2.ClientAllInfo(ip,port,type_lock)
        elif file_name in self.SHARE_LOCK:
            for tip,tport,t_lock in self.SHARE_LOCK[file_name]:
                yield lock_pb2.ClientAllInfo(tip,tport,t_lock)

        else:
            yield lock_pb2.ClientAllInfo('','',0)

    def lock_file(self, request, context):
        """给文件加锁
        args: filename:string, clientInfo:IP,port
        """
        result = 0

        file_name = request.filename
        type_lock = request.typelock

        temp = context.peer().split(':')
        #print("temp: ",temp)
        IP = temp[1]
        port = temp[2]
        if type_lock == 2:
            if file_name in self.SHARE_LOCK or file_name in self.EXCLUSIVE_LOCK:
                result = 0
            else:
                result = 2
                self.EXCLUSIVE_LOCK[file_name] = (IP,port,type_lock)
        elif type_lock == 1:
            if file_name in self.EXCLUSIVE_LOCK:
                result = 0
            elif file_name in self.SHARE_LOCK:
                result = 1
                self.SHARE_LOCK[file_name].append((IP,port,type_lock))
            else:
                result = 1
                self.SHARE_LOCK[file_name] = [(IP,port,type_lock)]
            
        return lock_pb2.TypeLock(typelock=result)

    def unlock_file(self, request, context):
        """给文件释放锁
        """
        result = 0
        file_name = request.filename
        type_lock = request.typelock
        temp = context.peer().split(':')
        #print("temp: ",temp)
        IP = temp[1]
        port = temp[2]

        if type_lock == 2:
            del self.EXCLUSIVE_LOCK[file_name]
            result = 1
        else:
            index0 = 0
            print(self.SHARE_LOCK)
            
            for index,(tip,tport,type_l) in enumerate(self.SHARE_LOCK[file_name]):
                if tip == IP and port == tport:
                     index0 = index
                     break
            del self.SHARE_LOCK[file_name][index0]
            if self.SHARE_LOCK[file_name] == []:
                del self.SHARE_LOCK[file_name]
            result = 1
        return lock_pb2.TypeLock(typelock=result)
        

def run():
    lock_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    lock_pb2_grpc.add_LockServicer_to_server(
        LockServer(),lock_server )
    lock_server.add_insecure_port('127.0.0.1:50051')
    lock_server.start()
    lock_server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    run()
        
    
        
    
    
    
    