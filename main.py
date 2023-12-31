#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@file: pyqt_gui.py
@author: Kilien
@time: 2023-07-19 10:35:10
@mail: kilienazure@gmail.com
"""

from wereader import *
from excel_func import *
import sys
import os
import time
from tqdm import tqdm
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile

# 设置header
HEADERS = {
    'Host': 'i.weread.qq.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

# 微信读书用户id
USER_VID = 0
# 文件路径
file=''
cookie_file = os.getcwd() + "\\temp\\cookie.txt"


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.DomainCookies = {}

        self.setWindowTitle('微信读书助手') # 设置窗口标题
        self.resize(900, 600) # 设置窗口大小
        self.setWindowFlags(Qt.WindowMinimizeButtonHint) # 禁止最大化按钮
        self.setFixedSize(self.width(), self.height()) # 禁止调整窗口大小

        url = 'https://weread.qq.com/#login' # 目标地址
        self.browser = QWebEngineView() # 实例化浏览器对象

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.cookieStore().deleteAllCookies() # 初次运行软件时删除所有cookies
        self.profile.cookieStore().cookieAdded.connect(self.onCookieAdd) # cookies增加时触发self.onCookieAdd()函数

        self.browser.loadFinished.connect(self.onLoadFinished) # 网页加载完毕时触发self.onLoadFinished()函数

        self.browser.load(QUrl(url)) # 加载网页
        self.setCentralWidget(self.browser) # 设置中心窗口





    # 网页加载完毕事件
    def onLoadFinished(self):

        global USER_VID
        global HEADERS

        # 获取cookies
        cookies = ['{}={};'.format(key, value) for key,value in self.DomainCookies.items()]
        cookies = ' '.join(cookies)
        # 添加Cookie到header
        HEADERS.update(Cookie=cookies)

        # 判断是否成功登录微信读书
        if login_success(HEADERS):
            #判断temp文件夹是否存在，不存在则创建
            temp_dir = os.getcwd() + "\\temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            #登录成功后写入cookie
            with open(cookie_file, 'w',encoding='utf-8') as f:
                f.write(cookies)
            print('登录微信读书成功!')

            # 获取用户user_vid
            if 'wr_vid' in self.DomainCookies.keys():
                USER_VID = self.DomainCookies['wr_vid']
                print('用户id:{}'.format(USER_VID))

                # 注入javascript脚本，与网页交互
                self.browser.page().runJavaScript('alert("登录成功！")')

                # 关闭整个qt窗口
                self.close()

        else:
            self.profile.cookieStore().deleteAllCookies()
            print('请扫描二维码登录微信读书...')




    # 添加cookies事件
    def onCookieAdd(self, cookie):
        if 'weread.qq.com' in cookie.domain():
            name = cookie.name().data().decode('utf-8')
            value = cookie.value().data().decode('utf-8')
            if name not in self.DomainCookies:
                self.DomainCookies.update({name: value})




    # 窗口关闭事件
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """

        self.setWindowTitle('退出中……')  # 设置窗口标题

        # 关闭软件软件之前删除所有cookies
        # 此代码不可删除，否则下次打开软件会自动加载浏览器中旧的cookies
        self.profile.cookieStore().deleteAllCookies()




if __name__=='__main__':
    #cookie文件存在时尝试从文件中读取cookie登录
    if os.path.exists(cookie_file) and os.path.isfile(cookie_file):
        #读取
        with open(cookie_file,'r',encoding='utf-8') as f:
            cookie_in_file = f.readlines()
        #尝试登陆
        headers_from_file = HEADERS
        headers_from_file.update(Cookie=cookie_in_file[0])
        if login_success(headers_from_file):
            print('登录微信读书成功!')
            #登录成后更新headers
            HEADERS = headers_from_file
            # headers_p.update(Cookie=cookie_in_file[0])
            #获取用户user_vid
            for item in cookie_in_file[0].split(';'):
                if item.strip()[:6] == 'wr_vid':
                    USER_VID = int(item.strip()[7:])
        else:
            app = QApplication(sys.argv) # 创建应用
            window = MainWindow() # 创建主窗口
            window.show() # 显示窗口
            app.exec_() # 运行应用，并监听事件
    #文件不存在时再启用登录界面
    else:
        app = QApplication(sys.argv) # 创建应用
        window = MainWindow() # 创建主窗口
        window.show() # 显示窗口
        app.exec_() # 运行应用，并监听事件


    # 创建目录
    data_dir = './导出资料/'
    note_dir = data_dir + '我的笔记/'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if not os.path.exists(note_dir):
        os.makedirs(note_dir)



    books = get_bookshelf(USER_VID, HEADERS) # 获取书架上的书籍
    books_finish_read = books['finishReadBooks']

    books_finish_read = [[book.bookId, book.title, book.author, book.cover] for book in books_finish_read]
    books_recent_read = books['recentBooks']
    books_recent_read = [[book.bookId, book.title, book.author, book.cover] for book in books_recent_read]
    books_all = books['allBooks']
    books_all = [[book.bookId, book.title, book.author, book.cover] for book in books_all]
    write_excel_xls(data_dir + '我的书架.xls', ['已读完的书籍', '最近阅读的书籍', '所有的书籍'], [["ID", "标题", "作者", "封面"], ]) # 写入excel文件
    write_excel_xls_append(data_dir + '我的书架.xls', '已读完的书籍', books_finish_read) # 追加写入excel文件
    write_excel_xls_append(data_dir + '我的书架.xls', '最近阅读的书籍', books_recent_read)  # 追加写入excel文件
    write_excel_xls_append(data_dir + '我的书架.xls', '所有的书籍', books_all)  # 追加写入excel文件



    # 获取【已读完的书籍】的笔记，如果想获取所有书籍的笔记，
    # 请自行更改books_finish_read为books_all
    pbar = tqdm(books_finish_read)
    for book in pbar:
        book_id = book[0]
        book_name = book[1]

        # 失败重试，最大重试次数为3
        for try_count in range(3):
            try:
                pbar.set_description("正在导出笔记【{}】".format(book_name))
                notes = get_bookmarklist(book_id, HEADERS)
                if (len(notes) == 0):
                    pbar.set_description("【{}】无想法".format(book_name))
                    break
                with open(note_dir + book_name + '.md', 'w', encoding='utf-8') as f:
                    f.write(notes)

                # 写入成功后跳出循环，防止重复写入
                break
            except Exception as e:
                # 忽略异常，直接重试
                pbar.set_description("获取笔记【{}】失败，开始第{}次重试".format(book_name, try_count + 1))
                print(f'caught {type(e)}: e')
                # 等待3秒后再重试
                time.sleep(3)
