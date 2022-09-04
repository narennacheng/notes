# -*- coding:utf-8 -*-
# @FileName  : wsgi_server.py
# @Date      : 2022/8/27 18:50
# @Author    : long
import datetime
import socket
import sys
from io import StringIO


def app(environ, start_response):
    """
    environ: 包含请求信息及环境信息的字典
    start_response: 接受两个参数`status, response_headers`的方法
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world']


class WSGIServer:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5

    application = None

    def __init__(self, server_address):
        self.socket = socket.socket(self.address_family, self.socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(server_address)
        self.socket.listen(self.request_queue_size)
        self.host, self.port = self.socket.getsockname()[:2]

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        while True:
            self.conn, client_address = self.socket.accept()
            self.handle_request()

    def handle_request(self):
        self.request_data = self.conn.recv(1024).decode()
        self.request_lines = self.request_data.splitlines()
        try:
            self.get_url_parameter()
            env = self.get_environ()
            app_data = self.application(env, self.start_response)
            self.finish_response(app_data)
            print('[{0}] "{1}" {2}'.format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.request_lines[0],
                self.status
            ))
        except Exception as e:
            raise e

    def get_url_parameter(self):
        self.request_dict = {"Path": self.request_lines[0]}
        for itm in self.request_lines[1:]:
            if ":" in itm:
                self.request_dict[itm.split(":")[0]] = itm.split(':')[1]
        self.request_method, self.path, self.request_version = self.request_dict.get("Path").split()

    def get_environ(self):
        env = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO(self.request_data),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'REQUEST_METHOD': self.request_method,
            'PATH_INFO': self.path,
            'SERVER_NAME': self.host,
            'SERVER_PORT': self.port,
            'USER_AGENT': self.request_dict.get('User-Agent')
        }
        return env

    def start_response(self, status, response_headers):
        headers = [
            ('Date', datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('Server', 'RAPOWSGI0.1')
        ]
        self.headers = response_headers + headers
        self.status  = status

    def finish_response(self, app_data):
        try:
            response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
            for header in self.headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in app_data:
                response += data
            self.conn.sendall(response.encode())
        finally:
            self.conn.close()


class UAMiddleware:
    """中间件：简单过滤ua"""
    def __init__(self, application):
        self.application = application

    def __call__(self, env, start_response):
        if 'curl' in env.get('USER_AGENT'):
            start_response('403 Not Allowed', [])
            return ["not allowed!"]
        return self.application(env, start_response)


def run(address, application):
    """
    run: python wsgi_server.py wsgi_server.app 8000
    """
    httpd = WSGIServer(address)
    httpd.set_app(UAMiddleware(application))
    print('RAPOWSGI Server Serving HTTP service on {}'.format(address))
    print('{0}'.format(datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')))
    httpd.serve_forever()


if __name__ == '__main__':
    port = '', 8080
    if len(sys.argv) < 2:
        sys.exit('请提供可用的wsgi应用程序, 格式为: 模块名.应用名 端口号')
    elif len(sys.argv) > 2:
        port = sys.argv[2]
    app_path = sys.argv[1]
    module_name, app_func_name = app_path.split('.')
    module = __import__(module_name)
    run(
        ('', int(port)),
        getattr(module, app_func_name)
    )
