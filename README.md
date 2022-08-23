# 个人笔记

> 文档初衷：在学习[PegasusWang](https://github.com/PegasusWang)的优秀笔记后，自己也想记录一些内容供自己学习使用。

### 本电子书制作和写作方式
使用 mkdocs 和 markdown 构建，使用  Python-Markdown-Math 完成数学公式。

mkdocs 使用：https://markdown-docs-zh.readthedocs.io/zh_CN/latest/

markdown 语法参考：http://xianbai.me/learn-md/article/about/readme.html

安装依赖：
```sh
# 方式1：
pip install mkdocs    # 制作电子书, http://markdown-docs-zh.readthedocs.io/zh_CN/latest/
# https://stackoverflow.com/questions/27882261/mkdocs-and-mathjax/31874157
pip install https://github.com/mitya57/python-markdown-math/archive/master.zip

# 推荐方式2：
pip install -r requirements.txt
```

编写并查看：
```sh
mkdocs serve     # 修改自动刷新浏览器，浏览器打开 http://localhost:8000 访问
# 数学公式参考 https://www.zybuluo.com/codeep/note/163962
# 图片最好压缩再放到仓库(不过不建议放非文本文件)
mkdocs gh-deploy    # 部署到自己的 github pages, 如果是 readthedocs 会自动触发构建
```

### 访问:

https://narennacheng.github.io/notes/

