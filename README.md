# 分布式系统项目报告

## 实验名称

分布式文件系统设计

## 实验题目

​		设计一个分布式文件系统。该文件系统可以是 client-server 架构，也可以是 P2P 非集中式架构。 要求文件系统，具有基本的访问、打开、删除、缓存等功能，同时具有一致性、支持多用户特点。 在设计过程中能够体现在分布式课程中学习到的一些机制或者思想，例如 Paxos 共识、缓存更新机制、访问控制机制、并行扩展等。

### 基本要求

- 文件系统中不同节点之间的通信方式采用 RPC 模式，可选择 Python 版本的 RPC、gRPC 等；
- 文件系统具备基本的文件操作模型包括：创建、删除、访问等功能；
- 作为文件系统的客户端要求具有缓存功能即文件信息首先在本地存储搜索，作为缓存的介质可以是内存也可以是磁盘文件； 
- 为了保证数据的可用性和文件系统性能，数据需要创建多个副本，且在正常情况下，多个副本不在同一物理机器，多个副本之间能够保持一致性（可选择最终一致性即延迟一致性也可以选择瞬时一致性即同时写）； 

- 支持多用户即多个客户端，文件可以并行读写（即包含文件锁） 

## 思路和解决方案

### 分布式文件系统架构设计

​		本项目中的分布式系统由4部分组成，分别是完全客户端totalClient, 文件服务器fileServer, 文件路径管理服务器direcrotyServer, 锁服务器lockingServer。它们之间的通信均采用gRPC进行通信。它们的具体功能以及具体的实现组织方式如下所述。

#### 1. 完全客户端totalClient

​		完全客户端是一个实现了整个文件系统从客户端输入指令到最终反馈给用户的程序。它负责处理并执行用户输入的指令，并最终在终端显示指令输出的结果。完全客户端执行指令的结果如下：

- 客户端totalClient读取用户的输入指令
- 客户端totalClient根据用户指令输入，执行特定的逻辑功能，调用不同的远程过程调用函数。比如，调用directoryServer的RPC,从而查询到要实际访问的文件的实际IP和端口号。
- 客户端根据用户的输入指令，调用lockServer的RPC，从而查询到要访问的文件的相关加锁的信息
- 客户端根据用户的directoryServer返回的IP和端口号，接着去调用fileServer的RPC,从而获取到要访问的文件内容。

#### 2. 文件服务器fileServer

​		文件服务器fileServer负责存储具体的用户的文件，在本项目中存在多个文件服务器，这些服务器均受到文件路径管理服务器directoryServer的管理。

​		文件服务器fileServer实现的基本功能包括：存储文件，读文件，写文件，删除文件。实验中，创建了3个文件服务器，它们之间的数据一致性方式采用的是瞬时一致性，即每次一个进程修改其中任何一个fileServer上的数据时，均会把这次改变立刻发往其他的fileServer。

#### 3. 锁服务器lockServer

​		锁服务器lockServer用于管理文件的锁，它将记录每个文件的加锁状态，从而控制并发冲突访问同一个文件的问题。实验中，设计了两种锁：共享锁（share）和排他锁（exclusive）。共享锁是进行读操作时，对文件加的锁，共享锁对所有共享锁都是相容的，即可以有多个读操作对同一个文件加共享锁；而排他锁则是进行写操作时，对文件加的锁，排他锁和所有锁都不相容，即写操作与任何其他操作互斥。

​		项目中，只有一个锁服务器。锁服务器lockServer实现的基本功能时：查询一个文件是否加锁、加了何种类型的锁，对特定文件进行加锁和解锁。

## 运行方法

进入code目录：
分别打开2个终端，然后在各自终端下运行2个服务器：
./code/
python directory.py
python lock_server.py
然后进入FILE_SERCER下的50057，50058，50059分别运行
./code/FILE_SERCER/
python file_server.py

最后在 ./code/下：
python total_client.py
python total_client2.py
