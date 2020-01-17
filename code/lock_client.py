from __future__ import print_function

import random
import logging
import grpc

import lock_pb2
import lock_pb2_grpc
import os

class LockClient(object):

    def __init__(self,channel):
        self.lock_server_stub = lock_pb2_grpc.LockStub(channel)
        
    def lock_exist_test(self,file_name):
        '''
        判断文件是否加锁,0不加锁，1共享锁，2互斥锁
        '''
        temp = lock_pb2.Str(filename=file_name)
        result = self.lock_server_stub.lock_exist_test(temp).typelock
        
        return result

    def lock_file(self,file_name,type_lock):
        '''
        对文件加锁，1表示共享锁，2表示排他锁
        returns:
            0:失败
            1:成功
        '''
        type_lock += 1
        temp = lock_pb2.ClientInfo(filename=file_name,typelock=type_lock)
        result = self.lock_server_stub.lock_file(temp).typelock

        if result == type_lock:
            return True
        return False
        
    def unlock_file(self,file_name,type_lock):
        '''
        对文件进行解锁，True成功，False失败
        '''
        temp = lock_pb2.ClientInfo(filename=file_name,typelock=type_lock)
        result = self.lock_server_stub.unlock_file(temp).typelock
        
        return result





if __name__ == '__main__':
    pass

    
        
    