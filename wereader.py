#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@file: wereader.py
@author: Kilien
@time: 2023-07-19 10:30:28
@mail: kilienazure@gmail.com
"""

"""
@origin: https://github.com/arry-lee/wereader
@author: arry-lee
@annotation: modified from arry-lee
"""

from collections import namedtuple, defaultdict
from operator import itemgetter
from itertools import chain

import requests
import json
import clipboard
import urllib3
# 禁用安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 书籍信息
Book = namedtuple('Book', ['bookId', 'title', 'author', 'cover'])



def get_bookmarklist(bookId, headers):
    """获取某本书的笔记返回md文本"""
    url = "https://i.weread.qq.com/book/bookmarklists?bookId=" + bookId

    data = request_data(url, headers)

    chapters = {c['chapterUid']: c['title'] for c in data['chapters']}
    contents = defaultdict(list)

    for item in sorted(data['updated'], key=lambda x: x['chapterUid']):
        # for item in data['updated']:
        chapter = item['chapterUid']
        text = item['markText']
        create_time = item["createTime"]
        start = int(item['range'].split('-')[0])
        contents[chapter].append((start, text))

    chapters_map = {title: level for level, title in get_chapters(int(bookId), headers)}
    res = ''
    for c in sorted(chapters.keys()):
        title = chapters[c]
        res += '#' * chapters_map[title] + ' ' + title + '\n'
        for start, text in sorted(contents[c], key=lambda e: e[0]):
            res += '> ' + text.strip() + '\n\n'
        res += '\n'

    return res

"""
(按顺序)获取书中的所有个人想法(Markdown格式,含原文,标题分级,想法前后缀)
"""
def get_mythought(bookId, headers):
    res = ''
    """获取数据"""
    if '_' in bookId:
        url = 'https://i.weread.qq.com/review/list?listtype=6&mine=1&bookId=' + bookId + '&synckey=0&listmode=0'
        data = request_data(url, headers)
        print('公众号暂时不支持获取想法')
        return ''
    else:
        url = "https://i.weread.qq.com/review/list?bookId=" + bookId + "&listType=11&mine=1&synckey=0&listMode=0"
        data = request_data(url, headers)
        # return 

    chapter_list = get_sorted_chapters(bookId, headers)

    thoughts_list = []
    for item in data['reviews']:
        title = '完书想法'
        level = 2
        chapterUid = 99999
        abstract = ''
        
        # 判断是否有摘要字段
        if ('abstract' in item['review']):
            # 摘要为空
            if (len(item['review']['abstract']) != 0):
              #获取想法所在章节id
              chapterUid = item['review']['chapterUid']
              #获取原文内容
              abstract = item['review']['abstract']
        else:
            chapterUid = 99999
            abstract = ''

        #获取标题
        for id, chapter in enumerate(chapter_list):
            if (chapter['chapterUid'] == chapterUid):
                title = chapter['title']
                level = chapter['level']
                
        #获取想法
        content = item['review']['content']
        
        # print('title..'+title)
        thoughts_list.append({'chapterUid':chapterUid, 'title':title, 'level':level, 'abstract':abstract, 'content':content})
    
    # 根据章节重新排序
    new_thoughts = sorted(thoughts_list, key=lambda x:x['chapterUid'], reverse=False)
    chapters_map = {1: "## ", 2: "### ", 3: "#### "}
    
    for k,it in enumerate(new_thoughts):
        # 标题
        res += chapters_map[it['level']] + it['title'] + '\n\n'
        # 摘要
        if (len(it['abstract']) != 0):
            res += "> " + it['abstract'] + '\n\n' 
        # 想法
        res += "```\n" + it['content'] + "\n```" + '\n\n'
    return res

"""
(按顺序)获取书中的章节：
[{'chapterUid': 1, 'level': 1, 'title': '封面'}
{'chapterUid': 153, 'level': 1, 'title': '版权信息'}]
"""
def get_sorted_chapters(bookId, headers):
    if '_' in bookId:
        print('公众号不支持输出目录')
        return ''
    url = "https://i.weread.qq.com/book/chapterInfos?" + "bookIds=" + bookId + "&synckeys=0"
    data = request_data(url, headers)
    chapters = []
    #遍历章节,章节在数据中是按顺序排列的，所以不需要另外排列
    for item in data['data'][0]['updated']:
        #判断item是否包含level属性。
        try:
            chapters.append({"chapterUid":item['chapterUid'],"level":item['level'],"title":item['title']})
        except:
            chapters.append({"chapterUid":item['chapterUid'],"level":1,"title":item['title']})
    return chapters


def get_bestbookmarks(bookId, headers):
    """获取书籍的热门划线,返回文本"""
    url = "https://i.weread.qq.com/book/bestbookmarks"
    params = dict(bookId=bookId)
    r = requests.get(url, params=params, headers=headers, verify=False)
    if r.ok:
        data = r.json()
        # clipboard.copy(json.dumps(data, indent=4, sort_keys=True))
    else:
        raise Exception(r.text)
    chapters = {c['chapterUid']: c['title'] for c in data['chapters']}
    contents = defaultdict(list)
    for item in data['items']:
        chapter = item['chapterUid']
        text = item['markText']
        contents[chapter].append(text)

    chapters_map = {title: level for level, title in get_chapters(int(bookId))}
    res = ''
    for c in chapters:
        title = chapters[c]
        res += '#' * chapters_map[title] + ' ' + title + '\n'
        for text in contents[c]:
            res += '> ' + text.strip() + '\n\n'
        res += '\n'
    return res


def get_chapters(bookId, headers):
    """获取书的目录"""
    url = "https://i.weread.qq.com/book/chapterInfos"
    data = '{"bookIds":["%d"],"synckeys":[0]}' % bookId

    r = requests.post(url, data=data, headers=headers, verify=False)

    if r.ok:
        data = r.json()
        clipboard.copy(json.dumps(data, indent=4, sort_keys=True))
    else:
        raise Exception(r.text)

    chapters = []
    for item in data['data'][0]['updated']:
        if 'anchors' in item:
            chapters.append((item.get('level', 1), item['title']))
            for ac in item['anchors']:
                chapters.append((ac['level'], ac['title']))

        elif 'level' in item:
            chapters.append((item.get('level', 1), item['title']))

        else:
            chapters.append((1, item['title']))

    return chapters


def get_bookinfo(bookId, headers):
    """获取书的详情"""
    url = "https://i.weread.qq.com/book/info"
    params = dict(bookId=bookId)
    r = requests.get(url, params=params, headers=headers, verify=False)

    if r.ok:
        data = r.json()
    else:
        raise Exception(r.text)
    return data


def get_bookshelf(userVid, headers):
    """获取书架上所有书"""
    url = "https://i.weread.qq.com/shelf/friendCommon"
    params = dict(userVid=userVid)
    r = requests.get(url, params=params, headers=headers, verify=False)
    if r.ok:
        data = r.json()
    else:
        raise Exception(r.text)

    books_finish_read = set() # 已读完的书籍
    books_recent_read = set() # 最近阅读的书籍
    books_all = set() # 书架上的所有书籍

    for book in data['finishReadBooks']:
        if ('bookId' not in book.keys()) or (not book['bookId'].isdigit()):  # 过滤公众号
            continue
        b = Book(book['bookId'], book['title'], book['author'], book['cover'])
        books_finish_read.add(b)
    books_finish_read = list(books_finish_read)
    books_finish_read.sort(key=itemgetter(-1)) # operator.itemgetter(-1)指的是获取对象的最后一个域的值，即以category进行排序



    for book in data['recentBooks']:
        if ('bookId' not in book.keys()) or (not book['bookId'].isdigit()): # 过滤公众号
            continue
        b = Book(book['bookId'], book['title'], book['author'], book['cover'])
        books_recent_read.add(b)
    books_recent_read = list(books_recent_read)
    books_recent_read.sort(key=itemgetter(-1)) # operator.itemgetter(-1)指的是获取对象的最后一个域的值，即以category进行排序


    books_all = books_finish_read + books_recent_read

    return dict(finishReadBooks=books_finish_read, recentBooks=books_recent_read, allBooks=books_all)


def get_notebooklist(headers):
    """获取笔记书单"""
    url = "https://i.weread.qq.com/user/notebooks"
    r = requests.get(url, headers=headers, verify=False)

    if r.ok:
        data = r.json()
    else:
        raise Exception(r.text)
    books = []
    for b in data['books']:
        book = b['book']
        b = Book(book['bookId'], book['title'], book['author'], book['cover'])
        books.append(b)
    books.sort(key=itemgetter(-1))
    return books


def login_success(headers):
    """判断是否登录成功"""
    url = "https://i.weread.qq.com/user/notebooks"
    r = requests.get(url,headers=headers,verify=False)

    if r.ok:
        return True
    else:
        return False

def request_data(url, headers):
    """由url请求数据"""
    r = requests.get(url,headers=headers,verify=False)
    if r.ok:
        data = r.json()
    else:
        raise Exception(r.text)
    return data