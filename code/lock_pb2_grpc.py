# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import lock_pb2 as lock__pb2


class LockStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.lock_exist_test = channel.unary_unary(
        '/Lock.Lock/lock_exist_test',
        request_serializer=lock__pb2.Str.SerializeToString,
        response_deserializer=lock__pb2.TypeLock.FromString,
        )
    self.get_lock_client = channel.unary_stream(
        '/Lock.Lock/get_lock_client',
        request_serializer=lock__pb2.Str.SerializeToString,
        response_deserializer=lock__pb2.ClientAllInfo.FromString,
        )
    self.lock_file = channel.unary_unary(
        '/Lock.Lock/lock_file',
        request_serializer=lock__pb2.ClientInfo.SerializeToString,
        response_deserializer=lock__pb2.TypeLock.FromString,
        )
    self.unlock_file = channel.unary_unary(
        '/Lock.Lock/unlock_file',
        request_serializer=lock__pb2.ClientInfo.SerializeToString,
        response_deserializer=lock__pb2.TypeLock.FromString,
        )


class LockServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def lock_exist_test(self, request, context):
    """判断文件是否加锁
    文件的名字，返回一个锁类型：0无锁，1共享锁，2互斥锁
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def get_lock_client(self, request, context):
    """获得加锁的文件的客户端信息
    args: filename
    returns: clientInfo: IP:string,port:string
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def lock_file(self, request, context):
    """给文件加锁
    args: filename:string, clientInfo:IP,port

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def unlock_file(self, request, context):
    """给文件释放锁
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_LockServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'lock_exist_test': grpc.unary_unary_rpc_method_handler(
          servicer.lock_exist_test,
          request_deserializer=lock__pb2.Str.FromString,
          response_serializer=lock__pb2.TypeLock.SerializeToString,
      ),
      'get_lock_client': grpc.unary_stream_rpc_method_handler(
          servicer.get_lock_client,
          request_deserializer=lock__pb2.Str.FromString,
          response_serializer=lock__pb2.ClientAllInfo.SerializeToString,
      ),
      'lock_file': grpc.unary_unary_rpc_method_handler(
          servicer.lock_file,
          request_deserializer=lock__pb2.ClientInfo.FromString,
          response_serializer=lock__pb2.TypeLock.SerializeToString,
      ),
      'unlock_file': grpc.unary_unary_rpc_method_handler(
          servicer.unlock_file,
          request_deserializer=lock__pb2.ClientInfo.FromString,
          response_serializer=lock__pb2.TypeLock.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Lock.Lock', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
