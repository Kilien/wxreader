# 微信读书个人助手

> 本项目基于 [@arry-lee](https://github.com/arry-lee) 的项目 [wereader](https://github.com/arry-lee/wereader/issues/20) 修改而来，并借鉴了 [@shengqiangzhang](https://github.com/shengqiangzhang) 的[一键导出微信读书的书籍和笔记](https://github.com/shengqiangzhang/examples-of-web-crawlers/tree/master/12. 一键导出微信读书的书籍和笔记)中的 GUI 登录方法，感谢原作者、感谢开源。

## 主要功能

1. 获取所有数据信息，导出Excel
2. 导出个人笔记想法

针对上面所获取的大多数内容，使用时有两方面的操作选择：一是输出到控制台并复制到剪切板；二是追加到指定文件。

主要代码见 `main.py`。

## 如何运行

首先确保已安装好依赖，然后在当前目录（wereader）执行以下命令：

```
# 跳转到当前目录
cd 目录名
# 先卸载依赖库
pip uninstall -y -r requirement.txt
# 再重新安装依赖库
pip install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 开始运行
python main.py
```


## License

MIT