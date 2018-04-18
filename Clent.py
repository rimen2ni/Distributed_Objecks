import requests
import time
import gevent
import multiprocessing
from multiprocessing import Queue,managers
from lxml import etree
import threading


process_num = 4 #进程数量
thread_num = 4 #线程数量


class QueueManager(multiprocessing.managers.BaseManager):
    pass

def download(url):# 请求网页，获取页面内容
    headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
    }
    html = requests.get(url,headers=headers)
    html.encoding = 'utf-8'
    return html.text

def parse_connect(html,con):#解析获取内容
    etr = etree.HTML(html)
    try:
        connects = etr.xpath('//div[@class="lemma-summary"]')
        connect = [' '.join(connect.xpath('.//div//text()')) for connect in connects ][0]#去掉内容之间的空格符，连接成一段语句
        if len(connect) == 0:#判断页面是否有内容，无内容则返回None
            con.put(None)
        con.put(connect)
    except:
        pass

def parse_titlea(html,titlea):#解析主标题
    etr = etree.HTML(html)
    title_a = etr.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()')[0]
    titlea.put(title_a)
    return title_a,type(title_a)

def parse_titleb(html,titleb):#解析副标题
    etr = etree.HTML(html)
    title_b = etr.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h2/text()')
    if len(title_b)==0:#判断页面是否有副标题，无内容则返回None
        title_b = None
    titleb.put(title_b)

def THERDER(queue_list,task):
    thread_list = []
    for i in range(thread_num):
        thr = threading.Thread(target=GEVENT,args=(queue_list,task))
        thr.start()
        thread_list.append(thr)
    for thread_one in thread_list:
        thread_one.join()


def GEVENT(queue_list,task):
    list_link = []
    gevent_list = []
    for i in range(100):  # 设置客服端爬取100条信息
        time.sleep(1)
        link = task.get()
        list_link.append(link)
        if link in list_link:  # url去重
            pass
        print('收到任务：%s' % link)

    for url in list_link:
       gevent_list.append(gevent.spawn(drew_url,queue_list,url))
    gevent.joinall(list_link)

def drew_url(queue_list,url):
    task,titlea,titleb,con = queue_list
    html = download(url)
    parse_titlea(html,titlea)
    parse_titleb(html,titleb)
    parse_connect(html,con)


if __name__ == '__main__':
    QueueManager.register('get_task') #注册通道函数,函数名必须与服务器注册的通道函数一样
    QueueManager.register('get_connects')
    QueueManager.register('get_titlea')
    QueueManager.register('get_titleb')
    QueueManager.register('get_close')

    manager = QueueManager(address=('10.36.131.47', 8848), authkey=123456)#链接服务器
    manager.connect()

    task = manager.get_task()#调用通道函数
    con = manager.get_connects()
    titlea = manager.get_titlea()
    titleb = manager.get_titleb()
    close = manager.get_close()

    queue_list = [task,titlea,titleb,con]
    process_list = []
    for i in range(process_num):
        mul = multiprocessing.Process(target=THERDER,args=(queue_list,task))
        mul.start()
        process_list.append(mul)
    for p in process_list:
        p.join()

    time.sleep(5)
    close.put(None)


