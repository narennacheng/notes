# 概念

**WSGI** 的全称 **web server gateway interface（web服务器网关接口）**，是一种规范协议，用于描述web服务器（如Nginx、uWSGI等服务器）如何与web应用程序（如Django、Flask）通信。



如何实现wsgi协议？

> server和application的规范在[PEP3333](https://peps.python.org/pep-3333/)中有具体描述，要实现WSGI协议，必须同时实现web server和web application，当前运行在WSGI协议之上的web框架有Flask, Django。。

# 

# uWSGI

文档：<https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html>

**uWSGI**是一个全功能的HTTP服务器。实现了WSGI协议、uwsgi协议、http协议等。主要作用是把HTTP协议转化成语言支持的网络协议，比如把HTTP协议转化成WSGI协议，让Python可以直接使用。

**uwsgi**（全小写）是 uWSGI 用来与其他服务器通信的本机二进制协议。



**uWSGI与与Nginx、django关系：**

- Nginx：反向代理、负载均衡、缓存静态资源。

- uWSGI 通常用于与Web 服务器（例如Nginx ）一起为PythonWeb 应用程序提供服务，这些服务器为uWSGI 的本机 uwsgi 协议提供直接支持

- 数据可能这样流动：brower => nginx => uWSGI => pythonWSGIModule => pythonApplication

  

## 简单使用

安装 `pip install uwsgi` 

测试：1.编写test.py，类似以下；2.启动`uwsgi --http :8080 --wsgi-file test.py`

```python
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello World"]
```

配置文件启动：

ini：`uwsgi --ini uwsgi.ini` 

xml: `uwsgi uwsgi.xml` 





## 配置选项

文档：<https://uwsgi-docs-zh.readthedocs.io/zh_CN/latest/Options.html>

ini格式参数说明

```ini
uid=www-data # Ubuntu系统下默认用户名
gid=www-data # Ubuntu系统下默认用户组
project=mysite1  # 项目名
base = /home/user1 # 项目根目录

home = %(base)/Env/%(project) # 设置项目虚拟环境,Docker部署时不需要
chdir=%(base)/%(project) # 设置工作目录
module=%(project).wsgi:application # wsgi文件位置

master=True # 主进程
processes=2 # 同时进行的进程数，一般

# 选项1, 使用unix socket与nginx通信，仅限于uwsgi和nginx在同一主机上情形
# Nginx配置中uwsgi_pass应指向同一socket文件
socket=/run/uwsgi/%(project).sock

# 选项2，使用TCP socket与nginx通信
# Nginx配置中uwsgi_pass应指向uWSGI服务器IP和端口
# socket=0.0.0.0:8000 或则 socket=:8000

# 选项3，使用http协议与nginx通信
# Nginx配置中proxy_pass应指向uWSGI服务器一IP和端口
# http=0.0.0.0:8000 

# socket权限设置
chown-socket=%(uid):www-data
chmod-socket=664

# 进程文件
pidfile=/tmp/%(project)-master.pid

# 以后台守护进程运行，并将log日志存于temp文件夹。
daemonize=/var/log/uwsgi/%(project).log 

# 服务停止时，自动移除unix socket和pid文件
vacuum=True

# 为每个工作进程设置请求数的上限。当处理的请求总数超过这个量，进程回收重启。
max-requests=5000

# 当一个请求花费的时间超过这个时间，那么这个请求都会被丢弃。
harakiri=60

#当一个请求被harakiri杀掉会，会输出一条日志
harakiri-verbose=true

# uWsgi默认的buffersize为4096，如果请求数据超过这个量会报错。这里设置为64k
buffer-size=65536

# 如果http请求体的大小超过指定的限制，打开http body缓冲，这里为64k
post-buffering=65536

#开启内存使用情况报告
memory-report=true

#设置平滑的重启（直到处理完接收到的请求）的长等待时间(秒)
reload-mercy=10

#设置工作进程使用虚拟内存超过多少MB就回收重启
reload-on-as=1024
```



xml格式样例

```xml
<uwsgi>
    <socket>:8000</socket>
    <listen>100</listen>
    <master>true</master>
    <processes>4</processes>
    <buffer-size>16384</buffer-size>
    <post-buffering>4096</post-buffering>
    <post-buffering-bufsize>16384</post-buffering-bufsize>
    <max-requests>1000</max-requests>
    <limit-as>1024</limit-as>
    <reload-mercy>3</reload-mercy>
    <harakiri>60</harakiri>
    <lazy/>
    <lock-engine>ipcsem</lock-engine>
    <log-maxsize>2147483647</log-maxsize>
    <log-slow>500</log-slow>
    <log-4xx/>
    <log-5xx/>
    <reload-on-as>512</reload-on-as>
    <reload-on-rss>512</reload-on-rss>
    <close-on-exec/>
    <cache2>name=my_site,items=10000,bitmap=1,blocksize=2000,sweep_on_full=1,lazy=1</cache2>
    <cache-expire-freq>6</cache-expire-freq>
    <cache-blocksize>2000</cache-blocksize>
    <chdir>/site/</chdir>
    <pythonpath>/site/</pythonpath>
    <env>DJANGO_SETTINGS_MODULE=Myapp.settings</env>
    <single-interpreter>true</single-interpreter>
    <thunder-lock/>
    <enable-threads>true</enable-threads>
    <wsgi-file>/site/Myapp/wsgi.py</wsgi-file>
</uwsgi>

```



## 部署与监控

### **与Nginx部署**

uWSGI和Nginx之间有多种通信方式, unix socket，http-socket和http。Nginx的配置必需与uwsgi配置保持一致。

选项1，如果你的nginx与uwsgi在同一台服务器上，优先使用本地机器的unix socket进行通信，这样速度更快。此时nginx的配置文件如下所示：

```nginx
location / {     
    include /etc/nginx/uwsgi_params;
    uwsgi_pass unix:/run/uwsgi/django_test1.sock;
}
```

选项2，如果nginx与uwsgi不在同一台服务器上，两者使用TCP socket通信，nginx可以使用如下配置：

```nginx
location / {     
    include /etc/nginx/uwsgi_params;
    uwsgi_pass uWSGI_SERVER_IP:8000;
}
```

选项3，如果nginx与uwsgi不在同一台服务器上，两者使用http协议进行通信，nginx配置应修改如下：

```nginx
location / {     
    # 注意：proxy_pass后面http必不可少哦！
    proxy_pass http://uWSGI_SERVER_IP:8000;
}
```



### 监测：

uwsgitop： <https://github.com/xrmx/uwsgitop>
django+uwsgi：<https://github.com/unbit/django-uwsgi>



