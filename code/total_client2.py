from __future__ import print_function
import random
import logging
import grpc
import os
import sys
import time
from file_client import FileClient
from lock_client import LockClient
from directory_client import DirectoryClient

DIRECTORY_IP = '127.0.0.1'
DIRECTORY_PORT = '50052'

LOCK_IP = '127.0.0.1'
LOCK_POT = '50051'
ROOT_PATH = './local2/'


def show_all():
    ## 查询路径服务器获得所有文件:
    with grpc.insecure_channel(str(DIRECTORY_IP)+':'+str(DIRECTORY_PORT)) as channel:
        directory_client = DirectoryClient(channel)
        temp = directory_client.get_all_file()
        print("-------------distribute system files-----------")
        for file_name,timestamp,host_id in temp:
            print('name:',file_name,'timestamp:',timestamp,'created:',host_id)
    for file_name in os.listdir(ROOT_PATH):
        print('name:',file_name,'created: local')
def real_read(file_name):
    ## 先在本地进行读
    try:
        file = os.path.join(ROOT_PATH,file_name)
        with open(file,'r',encoding='utf-8')as f:
            return f.read()
    except:
        return read(file_name)
def local_write(file_name,context):
    try:
        file = os.path.join(ROOT_PATH,file_name)
        with open(file,'w',encoding='utf-8')as f:
            f.write(context)
            return True
    except:
        return False

def read(file_name):

    ip,port,timestamp,host_id = (None,None,None,None)

    ## 查询锁控制服务器，查看该文件是否被加互斥锁
    with grpc.insecure_channel(str(LOCK_IP)+':'+str(LOCK_POT)) as channel:
        lock_client = LockClient(channel)
        # 0 无锁, 1为共享锁,2 为互斥锁
        result = lock_client.lock_exist_test(file_name)

        if(result == 2):
            return "Can't access this file, another client is writing!"
        else:
            ## 给文件加共享锁,0表示共享锁，1表示互斥锁
            if(lock_client.lock_file(file_name,0)):
                pass
            else:
                return "Unknown Error"

    ## 查询路径服务器获得文件所在的ip,port
    with grpc.insecure_channel(str(DIRECTORY_IP)+':'+str(DIRECTORY_PORT)) as channel:
        directory_client = DirectoryClient(channel)
        file_name,ip,port,timestamp,host_id = directory_client.get_file_address(file_name)
        if file_name == '':
            return "No such file"
        #print(ip,":",port)

    ## 访问文件服务器，访问文件
    result_str = ''
    with grpc.insecure_channel(str(ip)+':'+str(port)) as channel:
        file_client = FileClient(channel)
        #print(ip,":",port)
        result_str = file_client.read(file_name)

    
    ## 释放共享锁
    with grpc.insecure_channel(str(LOCK_IP)+':'+str(LOCK_POT)) as channel:
        lock_client = LockClient(channel)
        ## 给文件解锁,0表示共享锁，1表示互斥锁
        if(lock_client.unlock_file(file_name,0)):
            pass
        else:
            return "Unknown Error"

    return result_str
    
def upload(file_name):
    '''
    采用瞬时一致性通信模型
    '''
    ## 判断文件是否存在，如果存在，不允许上传
    with grpc.insecure_channel(str(DIRECTORY_IP)+':'+str(DIRECTORY_PORT)) as channel:
        directory_client = DirectoryClient(channel)
        tfile_name,ip,port,timestamp,host_id = directory_client.get_file_address(file_name)
        if tfile_name:
            return False
    
    t_file_name = os.path.join(ROOT_PATH,file_name)
    with open(t_file_name,'r',encoding='utf-8')as f:
        result_str = f.read()
    
        ## 获取所有的文件服务器的地址
        with grpc.insecure_channel(str(DIRECTORY_IP)+':'+str(DIRECTORY_PORT)) as channel:
            directory_client = DirectoryClient(channel)
            server_list = directory_client.get_all_server()

        ## 向所有的文件服务器写入该文件
        for ip,port in server_list:
            with grpc.insecure_channel(str(ip)+':'+str(port)) as channel:
                file_client = FileClient(channel)
                if not file_client.upload(file_name,result_str):
                    print("Unknown Error from",ip,port)
                else:
                    ## 把写入服务器文件的更新消息反馈给路径服务器
                    with grpc.insecure_channel(str(DIRECTORY_IP)+':'+str(DIRECTORY_PORT)) as channel:
                        directory_client = DirectoryClient(channel)
                        timestamp = time.time()
                        directory_client.add_file_address(file_name,ip,port,timestamp)
        return True

def download(file_name,new_name=None):
    if(new_name is None):
        new_name = file_name
    result_str = read(file_name)
    if result_str == "Unknown Error":
        print(result_str)
        return
    elif result_str == "Can't access this file, another client is writing!":
        print(result_str)
        return 
    elif result_str == 'No such file':
        print('No such file!')
        return
    else:
        file_name = os.path.join(ROOT_PATH,new_name)
        with open(file_name,'w',encoding='utf-8')as f:
            f.write(result_str)
            print("downloaded at",file_name)
            return 
def delete_local(file_name):
    file = os.path.join(ROOT_PATH,file_name)
    try:
        os.remove(file)
        return True
    except:
        return False
def delete(file_name):
    delete_local(file_name)
    ip,port,timestamp,host_id = (None,None,None,None)

    ## 查询锁控制服务器，查看该文件是否被加互斥锁
    with grpc.insecure_channel(str(LOCK_IP)+':'+str(LOCK_POT)) as channel:
        lock_client = LockClient(channel)
        # 0 无锁, 1为共享锁,2 为互斥锁
        result = lock_client.lock_exist_test(file_name)

        if(result != 0):
            return "Can't delete it! "
     
    ## 查询路径服务器获得文件所在的ip,port
    with grpc.insecure_channel(str(DIRECTORY_IP)+':'+str(DIRECTORY_PORT)) as channel:
        directory_client = DirectoryClient(channel)
        tfile_name,ip,port,timestamp,host_id = directory_client.get_file_address(file_name)
        if tfile_name == '':
            return "No such file!"
        temp = directory_client.get_file_all_address(file_name)
        timestamp = time.time()
        if( not directory_client.del_file_address(file_name,timestamp)):
            return "Unknown Error"

    ## 访问文件服务器，删除文件
    for ip,port in temp:
        with grpc.insecure_channel(str(ip)+':'+str(port)) as channel:
            file_client = FileClient(channel)
            result = file_client.delete(file_name)

    return True
    


if __name__ == '__main__':

    try:
        os.mkdir(ROOT_PATH)
    except:
        pass
    ## 用户交互界面 ##
    print("This is a distribute file system by shuitang!")
    print("copyright@ wangyk26@mail2.sysu.edu.cn")
    command = input(">>")
    NUM = 25
    while(command != 'quit'):

        if command == 'help':
            print("This is a distribute file systems by shuitang!")
            print("copyright@ wangyk26@mail2.sysu.edu.cn")
            print("ls" + (NUM-len("ls"))*'-' + "show the files")
            print("w" +(NUM-len("w"))*'-' + "write a file")
            print("r"+ (NUM-len("r"))*'-' + "read a file")
            print("up" + (NUM-len("up"))*'-' + "upload a file")
            print("do"+(NUM-len("do"))*'-' +"download a file")
            print("rm" + (NUM-len("rm"))*'-' + "delete a loal and remote file")
            print("rl" + (NUM-len("rl"))*'-' + "delete a local file")
        elif command == 'ls':
            #print("all the files: ")
            show_all()

        elif command == 'w':
            file_name = input("file name to write: ")
            s = input("file content to wirte: ")
            print(local_write(file_name,s))

        elif command == 'r':
            file_name = input("file name to read: ")
            print(real_read(file_name))

        elif command == 'rm':
            file_name = input("file name to delete: ")
            print(delete(file_name))
        elif command == 'rl':
            file_name = input("file name to delete: ")
            print(delete_local(file_name))
        elif command == 'up':
            file_name = input("file name to upload: ")
            upload(file_name)

        elif command == 'do':
            file_str = input("file name to download: ").split(' ')
            file_name = file_str[0]
            new_name = None
            if len(file_str) > 1:
                new_name = file_str[1]
            download(file_name,new_name)
       
        elif(command == ''):
            pass
        else:
            print("Invalid command, you can input 'help' to get help")
        command = ''
        command = input(">>")
