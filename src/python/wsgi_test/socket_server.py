# -*- coding:utf-8 -*-
# @FileName  : socket_server.py
# @Date      : 2022/8/27 17:49
# @Author    : long
import socket

host_port = ('127.0.0.1', 8000)


def server():
    # 1.初始化，使用IPv4和TCP通信协议
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 2.绑定地址端口
    s.bind(host_port)

    # 3.启动监听
    s.listen(1)
    print("server listening on %s:%s" % host_port)
    # 4.启动事件循环，接收请求
    while True:
        sock, addr = s.accept()
        data = sock.recv(1024)
        print("recv data: %s" % data)
        # sock.sendall(b"ok")
        sock.sendall("ok".encode('utf-8'))

        # 关闭
        sock.close()
        # if data.decode('utf-8').lower() == 'q':
        if "?exit=1" in data.decode('utf-8'):
            break
    s.close()


if __name__ == '__main__':
    server()
