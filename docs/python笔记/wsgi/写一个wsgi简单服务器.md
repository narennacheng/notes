> 参考：[自己写一个 wsgi 服务器运行 Django 、Tornado 等框架应用](https://segmentfault.com/a/1190000005640475)



## http server

首先编写一个http server，了解下通信流程：

server端：

- 初始化socker；
- 绑定套接字到端口（bind）；
- 监听端口（listen）；
- 接收连接请求（accept）；
- 通信（send/recv）；
- 关闭连接（close）；



client端：

- 初始化socket；
- 发出连接请求（connect）；
- 通信（send/recv）；
- 关闭连接（close）；



server示例代码：

```python
host_port = ('127.0.0.1', 8000)
# 1.初始化，使用IPv4和TCP通信协议
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 2.绑定地址端口
s.bind(host_port)
# 3.启动监听
s.listen(1)
print("server listening on %s:%s" % host_port)
# 4.启动事件循环，接收请求
i = 0
while i < 5:
    sock, addr = s.accept()
    data = sock.recv(1024)
    print("recv data: %s" % data)
    # sock.sendall(b"ok")
    sock.sendall("ok".encode('utf-8'))
    # 关闭
    sock.close()
    i += 1
s.close()

```

client端可以用curl或browser代替。





## wsgi server

编写一个标准的wsgi server需要遵循[PEP3333](https://peps.python.org/pep-3333/)规范去编写app和server。

### **application**

application需要接收两个参数`environ, start_reponse` 

以下就是简单的标准wsgi app示例：

```python
def application(environ, start_response):
    """
    environ: 包含请求信息及环境信息的字典
	start_response: 接受两个参数`status, response_headers`的方法
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world']
```



### **server**

server实现流程其实和上面httpserver的实现是一样，不同的是，我们需要将数据传入封装到environ中，然后丢到app应用中去处理，得到处理结果再返回。以下是简单实现例子

```python
import datetime
import socket
import sys
from io import StringIO


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


def run(address, application):
    """
    run: python wsgi_server.py app.app 8000
    """
    httpd = WSGIServer(address)
    httpd.set_app(application)
    print('RAPOWSGI Server Serving HTTP service on {}'.format(address))
    print('{0}'.format(datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')))
    httpd.serve_forever()


if __name__ == '__main__':
    port = '', 8000
    if len(sys.argv) < 2:
        sys.exit('请提供可用的wsgi应用程序, 格式为: 模块名.应用名 端口号')
    elif len(sys.argv) > 2:
        port = sys.argv[2]
    app_path = sys.argv[1]
    module, application = app_path.split('.')
    module = __import__(module)
    app = getattr(module, application)
    run(('', int(port)), app)

```

现在运行`python server.py app.application 8000`, 然后浏览器访问`localhost:8000`

> server运行过程解释：
>
> 1. 初始化，建立套接字，绑定监听端口；
> 2. 设置加载的 web app；
> 3. 开始持续运行 server；
> 4. 处理访问请求；
> 5. 获取请求信息及环境信息（`get_environ(self)`）；
> 6. 用`environ`运行加载的 web app 得到返回信息；
> 7. 构造返回信息头部；
> 8. 返回信息；





### middleware

中间件的作用就是在server拿到请求数据给app应用前，做一些特殊处理，比如验证、限流等等。

下面是个简单过滤ua的中间件例子

```python
class UAMiddleware:
    """中间件：简单过滤ua"""
    def __init__(self, application):
        self.application = application

    def __call__(self, env, start_response):
        if 'curl' in env.get('USER_AGENT'):
            start_response('403 Not Allowed', [])
            return ["not allowed!"]
        return self.application(env, start_response)

"""
# 然后在run方法set_app中调用， like this
def run(address, application):
    httpd = WSGIServer(address)
    httpd.set_app(UAMiddleware(application))
	...
"""
```





## Django WSGI

具体看以下实现类

[WSGIHandler](https://github.com/django/django/blob/main/django/core/handlers/wsgi.py)

[WSGIServer](https://github.com/django/django/blob/main/django/core/servers/basehttp.py)

[WSGIServer](https://docs.python.org/3/library/wsgiref.html#module-wsgiref.simple_server)

```python
# django\core\handlers\wsgi.py 
class WSGIHandler(base.BaseHandler):
    pass
    
# django\core\servers\basehttp.py
class WSGIServer(simple_server.WSGIServer):
    """BaseHTTPServer that implements the Python WSGI protocol"""
    pass


# wsgiref.simple_server.py
class WSGIServer(HTTPServer):

    """BaseHTTPServer that implements the Python WSGI protocol"""

    application = None

    def server_bind(self):
        """Override server_bind to store the server name."""
        HTTPServer.server_bind(self)
        self.setup_environ()

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''
        env['SCRIPT_NAME'] = ''

    def get_app(self):
        return self.application

    def set_app(self,application):
        self.application = application
```





## Tornado WSGI



tornado 直接从底层用 epoll 自己实现了 事件池操作、tcp server、http server，所以它是一个完全不同当异步框架，但 tornado 同样也提供了对 wsgi 对支持，不过这种情况下就没办法用 tornado 异步的特性了。

与其说 tornado 提供了 wsgi 支持，不如说它只是提供了 wsgi 兼容，tornado 提供两种方式：

#### WSGIContainer

其他应用要在 tornado server 运行， tornado 提供 [WSGIContainer](https://github.com/tornadoweb/tornado/blob/master/tornado/wsgi.py)。


#### WSGIAdapter

tornado 应用要在 wsgi server 上运行， tornado 提供 [WSGIAdapter](https://github.com/tornadoweb/tornado/blob/master/tornado/wsgi.py)



最后我们来试试让我们自己的服务器运行 tornado app

```python
# coding: utf-8
# tornado_wsgi.py

from __future__ import unicode_literals

import datetime
import tornado.web
import tornado.wsgi

from middleware import TestMiddle
from server import WSGIServer


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("this is a tornado wsgi application")


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    wsgi_app = tornado.wsgi.WSGIAdapter(application)
    server = WSGIServer(('', 9090))
    server.set_application(TestMiddle(wsgi_app))
    print('RAPOWSGI Server Serving HTTP service on port {0}'.format(9090))
    print('{0}'.format(datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'))）
    server.serve_forever()
```

运行：`python tornado_wsgi.py`，打开浏览器：`localhost:9090`，完美运行，中间件也运行正常

