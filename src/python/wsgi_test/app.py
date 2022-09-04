# -*- coding:utf-8 -*-
# @FileName  : app.py
# @Date      : 2022/8/27 19:36
# @Author    : long
def app(environ, start_response):
    """
    environ: 包含请求信息及环境信息的字典
    start_response: 接受两个参数`status, response_headers`的方法
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world']


