import requests
import multiprocessing
from multiprocessing import Queue,managers
import time
from lxml import etree
import smtplib
from email.mime.text import MIMEText

#定义队列
queue_task = Queue()
queue_connect = Queue()
queue_titlea = Queue()
queue_titleb = Queue()
queue_close = Queue()

def download(url):#下载页面内容
    headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
    }
    html = requests.get(url,headers=headers)
    html.encoding = 'utf-8'
    # print(html.text)
    return html

def parse_url(html):#解析页面a标签内以/item开头的所有链接
    etr = etree.HTML(html.text)
    links = etr.xpath('//a//@href')

    for link in links:
        if link.startswith('/item'):
            link = 'https://baike.baidu.com' + link
            print('传送任务：%s' % link)
            task.put(link)
    print('等候接收结果.....')

def email():#定义邮箱
    #设置邮件内容
    mimtext = MIMEText('爬虫结束请知悉')
    mimtext['subject'] = '爬虫结束请知悉'
    mimtext['to'] = 'rimen_luo@163.com'
    mimtext['from'] = 'rimen_luo@163.com'
    emailSever = smtplib.SMTP('smtp.163.com',25) #注册邮件服务器
    emailSever.login(user='rimen_luo',password='xxxxxx')
    emailSever.sendmail('rimen_luo@163.com','rimen_luo@163.com',mimtext.as_string())#发送邮件
    emailSever.close()

def retrun_task():
    return queue_task

def retrun_connect():
    return queue_connect

def retrun_titlea():
    return queue_titlea

def retrun_titleb():
    return queue_titleb

def retrun_close():
    return queue_close

class QueueManager(multiprocessing.managers.BaseManager):
    pass

if __name__ == '__main__':
    QueueManager.register('get_task',callable=retrun_task)#注册通道函数，给客户度调用
    QueueManager.register('get_connects',callable=retrun_connect)
    QueueManager.register('get_titlea',callable=retrun_titlea)
    QueueManager.register('get_titleb',callable=retrun_titleb)
    QueueManager.register('get_close',callable=retrun_close)

    manager = QueueManager(address=('10.36.131.47',8848),authkey=123456)#配置服务端
    manager.start()

    task = manager.get_task()#调用通道函数
    con = manager.get_connects()
    titlea = manager.get_titlea()
    titleb = manager.get_titleb()
    close = manager.get_close()

    url = 'https://baike.baidu.com/item/Python/407313'
    html = download(url)
    parse_url(html)

    close_q = 0#设置一个开关close_q，当一个客服端完成爬取任务时往通道queue_close发送一个None
    while close_q<=5:#开5个服务端则退出while循环的条件为close_q<=5
        cond = con.get()
        tla = titlea.get()
        tlb = titleb.get()
        # data = close.get()
        print('获取到的主标题：%s||副标题：%s'% (tla,tlb) )
        print('内容：%s'%cond )
        print( '\n')

        if close.qsize() != 0:#判断通道是否有信息,如果收到None则close_q自加1
            close_q += 1
    manager.shutdown()#任务完成关闭服务器
    email()#任务完成邮件通知





















