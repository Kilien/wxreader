from wereader import *
from excel_func import *
import sys
import os
import time
import json
import requests
from collections import namedtuple, defaultdict

requests.packages.urllib3.disable_warnings()
headers = {
    'Host': 'i.weread.qq.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie':''
}

# 微信读书用户id
USER_VID = 0
# 文件路径
file=''
cookie_file = os.getcwd() + "\\temp\\cookie.txt"

"""由url请求数据"""
def request_data(url):
    global headers
    r = requests.get(url,headers=headers,verify=False)
    if r.ok:
        data = r.json()
    else:
        raise Exception(r.text)
    return data

"""
(按顺序)获取书中的章节：
[(1, 1, '封面'), (2, 1, '版权信息'), (3, 1, '数字版权声明'), (4, 1, '版权声明'), (5, 1, '献给'), (6, 1, '前言'), (7, 1, '致谢')]
"""
def get_sorted_chapters(bookId, headers):
    if '_' in bookId:
        print('公众号不支持输出目录')
        return ''
    url = "https://i.weread.qq.com/book/chapterInfos?" + "bookIds=" + bookId + "&synckeys=0"
    data = request_data(url)
    chapters = []
    #遍历章节,章节在数据中是按顺序排列的，所以不需要另外排列
    for item in data['data'][0]['updated']:
        #判断item是否包含level属性。
        try:
            chapters.append({"chapterUid":item['chapterUid'],"level":item['level'],"title":item['title']})
        except:
            chapters.append({"chapterUid":item['chapterUid'],"level":1,"title":item['title']})
    return chapters

if __name__ == '__main__':
    #MP_WXS_3009174698
    bookId = '536972'
    bookmarklist_url = "https://i.weread.qq.com/book/bookmarklist?bookId=" + bookId
    my_MPthought_url = 'https://i.weread.qq.com/review/list?listtype=6&mine=1&bookId=' + bookId + '&synckey=0&listmode=0'
    my_bookthought_url = "https://i.weread.qq.com/review/list?bookId=" + bookId + "&listType=11&mine=1&synckey=0&listMode=0"
    best_bookmark_url = "https://i.weread.qq.com/book/bestbookmarks?bookId=" + bookId
    bookInfo_url = "https://i.weread.qq.com/book/info?bookId=" + bookId
    book_shelf_url = "https://i.weread.qq.com/shelf/sync?userVid=" + str(USER_VID) + "&synckey=0&lectureSynckey=0"
    notes_url = 'https://i.weread.qq.com/review/list?listType=6&userVid=' + str(USER_VID) + '&rangeType=2&mine=1&listMode=1'

    #cookie文件存在时尝试从文件中读取cookie登录
    if os.path.exists(cookie_file) and os.path.isfile(cookie_file):
        #读取
        with open(cookie_file,'r',encoding='utf-8') as f:
            cookie_in_file = f.readlines()
        #尝试登陆
        headers.update(Cookie=cookie_in_file[0])
        if login_success(headers):
            print('login successfully')
    else:
        print('no cookie...')

    data = request_data(my_bookthought_url)
    chapter_list = get_sorted_chapters(bookId, headers)
    # print(chapter_list)

    res = ''
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
    
    for k,it in enumerate(new_thoughts):
        print(it)
        res += "### " + it['title'] + '\n\n'
        res += "> " + it['abstract'] + '\n\n' + "```\n" + it['content'] + "\n```" + '\n\n'

    # data_dir = './导出资料/'
    # note_dir = data_dir + '我的笔记/'
    # with open(note_dir + 'test' + '.md', 'w', encoding='utf-8') as f:
    #     f.write(res)