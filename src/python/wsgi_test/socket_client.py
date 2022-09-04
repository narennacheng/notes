# -*- coding:utf-8 -*-
# @FileName  : socket_client.py
# @Date      : 2022/8/27 18:08
# @Author    : long
import socket

host_port = ('127.0.0.1', 8000)


def client():
    # 1.初始化
    # 使用IPv4和TCP通信协议
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 2.连接服务器
    s.connect(host_port)

    # 4.启动事件循环，发送请求
    while True:
        inp = input()
        s.sendall(inp.encode('utf-8'))
        if inp.lower() == 'q':
            break
    # 关闭
    s.close()


if __name__ == '__main__':
    client()
