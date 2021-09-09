"""
author:袁帅
date:2021/6/30 13:14
账号id、账号昵称、转发、评论、点赞；发布时间、发布内容、内容链接、账号主页链接
"""
# -*- coding=utf-8 -*-
# 导入模块
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import os
import sys
import time
from time import sleep
from urllib.parse import quote
import xlsxwriter
from lxml import etree
import random
import pymongo
from bs4 import BeautifulSoup
import locale
# 中文支持
locale.setlocale(locale.LC_CTYPE, 'chinese')


# 连接数据库
# from 转变时间戳 import time_turn

database = pymongo.MongoClient('192.168.1.103', port=27017)
db = database['facebook']
kzxy_list = db['kzxy']

sys.path.append(os.path.dirname(__file__))

from tools.logger_server import logger
from tools.selenium_server import SeleniumServer
from tools.extract import Extract
from settings import REDIS, EPR_TIME
from selenium.webdriver.common.keys import Keys


class FB:

    def __init__(self):

        self.selenium = SeleniumServer()
        self.driver = self.selenium.driver
        self.redis = REDIS

        self.logger = logger
        self.extract = Extract()

        self.epr_time = EPR_TIME

    def start(self, keyword,zong_sums,wsheet1):
        """程序的入口
        :param keyword 搜索的关键字

        """
        # 退出设置
        tc_sum = 1
        sums = zong_sums
        # 输出搜索日志
        self.logger.debug('start: {}'.format(keyword))
        # 打开首页
        home_url = 'https://www.facebook.com/{}'.format(keyword)
        try:
            # 打开facebook
            self.driver.get(home_url)
            sleep(random.randint(5, 7))
        except:
            pass
        # sleep(random.randint(3, 5))
        # # 输入关键字
        # self.driver.find_element_by_xpath('//input[@type="search"]').send_keys(keyword)
        # sleep(random.randint(2, 4))
        # # 鼠标确认
        # self.driver.find_element_by_xpath('//input[@type="search"]').send_keys(Keys.ENTER)

        # sleep(random.randint(2, 6))
        #
        # 如果有多个同名作者
        # 点击作者名
        # self.driver.find_element_by_xpath(
        #     '//span[@class="nc684nl6"]/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p dkezsu63"]').click()
        # sleep(random.randint(3, 6))
   
        # URL1 = self.driver.current_url
        # print('URL1',URL1)
        # 获取账号id
        # zh_id = URL1.split('/')[3]
        # # self.driver.get(home_url)
        # self.driver.get(URL1)
        # 从上一次读取的位置读取
        # 统计一个用户发帖数量
        num = 0
        sleep(random.randint(6, 8))
             # 一共下滑一百次次，下滑一次停顿0.5s
        # 由于是异步加载，所以需要拉到最下方
        zhnc = ''
        for i in range(1,2000):
            # 从第一页开始，没别的意思，强迫症
            print(f'*****************************第{i}页***************************')
            # self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            # self.driver.execute_script('window.scrollBy(0,250);')
            # sleep(random.randint(2, 3))
            self.driver.execute_script('window.scrollBy(0,2200)')
            sleep(random.randint(6, 8))

            # sleep(random.randint(2, 4))
            # sleep(random.randint(2, 5))
            # URL1 = self.driver.current_url
            # print('URL1',URL1)
            ## self.driver.get(home_url)
            # self.driver.get(URL1)
            # 获取网页源码
            html = etree.HTML(self.driver.page_source)
            # //div[@class="k4urcfbm"]/div/div
            # all_list = html.xpath('//div[@data-pagelet="ProfileTimeline"]/div')
            # 11111 
            try:
                # all_list = html.xpath('//div[@data-pagelet="ProfileTimeline"]/div[2]/div[@class=""]')
                all_list = html.xpath('//div[@class="k4urcfbm"]/div[2]/div[@class="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"]')
                if len(all_list) == 0:
                    # html = etree.HTML(self.driver.page_source)
                    
                    # all_list1 = html.xpath('//div[@class="k4urcfbm"]/div/div')
                    all_list1 = html.xpath('//div[@class="k4urcfbm"]/div[@class="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"]')
                    # print('all_list1',len(all_list1))
                    if len(all_list1) == 0:
                        # //div[@data-pagelet="ProfileTimeline"]/div[2]/div[@class=""]
                        all_list1 = html.xpath('//div[@data-pagelet="ProfileTimeline"]/div/div[@class="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"]')
                        print("****进入第二方案***",len(all_list1))

                        if len(all_list1) == 1:
                            self.driver.execute_script('window.scrollBy(0,-1800)')
                            sleep(random.randint(5, 8))
                            print('上划一下',tc_sum)
                            tc_sum += 1   
                            if tc_sum == 3:
                                print("<<<<<<<<共",num,"条数据<<<<<<<<<<<",keyword,"本月数据读取完毕,写入第",sums,"行,下一用户>>>>>>>>>>>>>>>>>")
                                self.driver.close()
                                return sums
                        elif len(all_list1) == 0:
                            print('无发帖',tc_sum)
                            tc_sum += 1   
                            if tc_sum == 3:
                                print("<<<<<<<<共",num,"条数据<<<<<<<<<<<",keyword,"本月数据读取完毕,写入第",sums,"行,下一用户>>>>>>>>>>>>>>>>>")
                                self.driver.close()
                                return sums
                        elif len(all_list1) == 3:
                            print('发帖3',tc_sum)
                            tc_sum += 1   
                            if tc_sum == 3:
                                print("<<<<<<<<共",num,"条数据<<<<<<<<<<<",keyword,"本月数据读取完毕,写入第",sums,"行,下一用户>>>>>>>>>>>>>>>>>")
                                self.driver.close()
                                return sums
                        da_list1 = all_list1[:-3]
                        for all_li in da_list1[num:len(da_list1)+1]:
                            # 临时储存数据的列表
                            list_shuju = []
                            # # 获取网页源码
                            # # 让时间元素出现在页面上
                            # # 将滚动条移动到页面的指定位置
                            # url3 = self.driver.find_element_by_xpath(
                            #     f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{num+1}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')

                            # ActionChains(self.driver).move_to_element(url3).perform()
                            # html = etree.HTML(self.driver.page_source)


                            # url4 = html.xpath(
                            #     f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a//@href')
                            # print('url4555555555555555',url4)


                            text = all_li.xpath(
                                './/div[@class="lzcic4wl"]//text()')
                            # print('text',text)
                            # # 贴子链接
                            # # //div[@data-pagelet="ProfileTimeline"]/div[1]//div[@class="j83agx80 cbu4d94t ew0dbk1b irj2b8pg"]/div[2]//@href
                            # try:
                            #     lianjie = all_list.xpath('.//div[@class="buofh1pr"]/div/div[2]//@href')[0]
                            #     print('帖子链接',lianjie)
                            # except:
                            #     print('全文本！')

                            # 账号昵称 //div[@class="qzhwtbm6 knvmm38d"]/span/h2/span/a/strong/span/text()
                            try:
                                zhnc = all_li.xpath(
                                    './/div[@class="qzhwtbm6 knvmm38d"]/span/h2/span/a/strong/span/text()')[0]
                                print(f'发布帐号昵称:{zhnc}')
                                list_shuju.append(zhnc)
                            except:
                                print(f'发布帐号昵称1:{zhnc}')
                                list_shuju.append(zhnc)

                            # 发布账号id
                            print('发布账号id',keyword)
                            list_shuju.append(keyword)
                                      

                            # 发布时间//div[@class="buofh1pr"]/div/div[2]/span/span/span[2]//text()
                            Time_list = all_li.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div/div/div[2]//div[@class="buofh1pr"]/div/div[2]/span/span/span[2]//text()')
                            time1 = ''
                            for Time in Time_list:
                                if Time == '=':
                                    continue
                                else:
                                    time1 += Time
                            print(time1)
                            try:
                                try:
                                    # 1小时转年月日
                                    TTime = time.time()
                                    xs = int(time1.split('小时')[0])
                                    sjc = xs * 60 * 60
                                    dp_time = TTime - sjc
                                    now_data = time.strftime('%m月%d日 %H:%M',time.localtime(dp_time))
                                    now_data = now_data[1:]
                                    print('now_data',now_data)
                                    list_shuju.append(now_data)
                                except:
                                    TTime = time.time()
                                    xs = int(time1.split('分钟')[0])
                                    sjc = xs * 60
                                    dp_time = TTime - sjc
                                    now_data = time.strftime('%m月%d日 %H:%M',time.localtime(dp_time))
                                    now_data = now_data[1:]
                                    print('now_data',now_data)
                                    list_shuju.append(now_data)
                            except:
                                if time1[0] == '8':

                                    print('本月发布时间：',time1)
                                    list_shuju.append(time1)
                                elif time1[0] == '昨':
                                    list_shuju.append(time1)
                                else:
                                    print("<<<<<<<<共",num,"条数据<<<<<<<<<<<",keyword,"本月数据读取完毕,写入第",sums,"行,下一用户>>>>>>>>>>>>>>>>>")
                                    self.driver.close()
                                    return sums

                            # 内容.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]//text()
                            content_data = all_li.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]//text()')
                            text = ''
                            for data in content_data:
                                if data == '=':
                                    continue
                                else:
                                    text += data
                            print('内容数据：',text)
                            list_shuju.append(text)


                            # 发布账号主页链接
                            list_shuju.append(home_url)

                            # # 标签
                            # short_pro = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[1]//text()')[0]
                                
                           

                            # # num += 1
                            # print(f'标签：{short_pro}')
                            # # 正文内容
                            # try:
                            #     content_data = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[3]//text()')[0]
                              
                            #     # num+=1
                            #     print('正文内容：',content_data)
                            # except:
                            #     content_data = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[2]//text()')[0]
                            #     print('正文内容：',content_data)

                            # 图片视频链接.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[3]/div[1]//@src

                            # 点赞
                            try:
                                love = all_li.xpath('.//span[@class="gpro0wi8 cwj9ozl2 bzsjyuwj ja2t1vim"]/span/span/text()')[0]
                                # num+=1

                                print('点赞数：',love)
                                list_shuju.append(int(love))
                            except:
                                print('无点赞！',0)
                                list_shuju.append(0)
                            # 分享评论
                            try:
                                comments_data = all_li.xpath('.//div[@class="bp9cbjyn j83agx80 pfnyh3mw p1ueia1e"]/div//span//text()')
                                print('comments_data',comments_data)
                                comm_shu = len(comments_data)
                                print(comm_shu)
                                if comm_shu == 2:
                                    for comm_data in comments_data:
                                        print('comm_data1234',comm_data)
                                        if comm_data[len(comm_data)-1] == '享':
                                            comm_data1 = int(comm_data.split('次')[0])
                                            print('分享数:',comm_data1)
                                            list_shuju.append(comm_data1)

                                        else:
                                            
                                            comm_data1 = int(comm_data.split('条')[0])
                                            print('评论数:',comm_data1)
                                            list_shuju.append(comm_data1)
                                elif comm_shu == 0:
                                    list_shuju.append(0)
                                    list_shuju.append(0)
                                else:
                                    for comm_data in comments_data:
                                        print('comm_data1234',comm_data)
                                        if comm_data[len(comm_data)-1] == '享':
                                            comm_data1 = int(comm_data.split('次')[0])
                                            list_shuju.append(0)
                                            print('评论数:',0)
                                            list_shuju.append(comm_data1)
                                            print('分享数:',comm_data1)

                                        else:

                                            comm_data1 = int(comm_data.split('条')[0])
                                            list_shuju.append(comm_data1)
                                            print('评论数:',comm_data1)    
                                            list_shuju.append(0)
                                            print('分享数:',0)                   
                            except:
                                print('分享评论有误！')
                                continue
                            print('+++list_shuju+++',list_shuju)
                            row = 'A' + str(sums)
                            wsheet1.write_row(row, list_shuju)
                            print('--------------第',num+1,'条数据！--------------------')
                            print('--------------写入到第',sums,'行数据！--------------------')
                            num+=1
                            sums +=1
                    else:  
                        print('all_list1',len(all_list1))
                        print("****进入第三方案***")
                        if len(all_list1) == 0:
                            tc_sum += 1   
                            if tc_sum == 3:
                                break 
                        da_list1 = all_list1[:-3]
                        for all_li in da_list1[num:len(da_list1)+1]:
                            # 临时储存数据的列表
                            list_shuju = []
                            # # 获取网页源码
                            # # 让时间元素出现在页面上
                            # # 将滚动条移动到页面的指定位置
                            # url3 = self.driver.find_element_by_xpath(
                            #     f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{num+1}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')

                            # ActionChains(self.driver).move_to_element(url3).perform()
                            # html = etree.HTML(self.driver.page_source)


                            # url4 = html.xpath(
                            #     f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a//@href')
                            # print('url4555555555555555',url4)


                            text = all_li.xpath(
                                './/div[@class="lzcic4wl"]//text()')
                            # print('text',text)
                            # # 贴子链接
                            # # //div[@data-pagelet="ProfileTimeline"]/div[1]//div[@class="j83agx80 cbu4d94t ew0dbk1b irj2b8pg"]/div[2]//@href
                            # try:
                            #     lianjie = all_list.xpath('.//div[@class="buofh1pr"]/div/div[2]//@href')[0]
                            #     print('帖子链接',lianjie)
                            # except:
                            #     print('全文本！')

                            # 账号昵称 //div[@class="qzhwtbm6 knvmm38d"]/span/h2/span/a/strong/span/text()
                            try:
                                zhnc = all_li.xpath(
                                    './/div[@class="qzhwtbm6 knvmm38d"]/span/h2/span/a/strong/span/text()')[0]
                                print(f'发布帐号昵称:{zhnc}')
                                list_shuju.append(zhnc)
                            except:
                                print(f'发布帐号昵称1:{zhnc}')
                                list_shuju.append(zhnc)

                            # 发布账号id
                            print('发布账号id',keyword)
                            list_shuju.append(keyword)
                                      

                            # 发布时间//div[@class="buofh1pr"]/div/div[2]/span/span/span[2]//text()
                            Time_list = all_li.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div/div/div[2]//div[@class="buofh1pr"]/div/div[2]/span/span/span[2]//text()')
                            time1 = ''
                            for Time in Time_list:
                                if Time == '=':
                                    continue
                                else:
                                    time1 += Time
                            print(time1)
                            try:
                                try:
                                    # 1小时转年月日
                                    TTime = time.time()
                                    xs = int(time1.split('小时')[0])
                                    sjc = xs * 60 * 60
                                    dp_time = TTime - sjc
                                    now_data = time.strftime('%m月%d日 %H:%M',time.localtime(dp_time))
                                    now_data = now_data[1:]
                                    print('now_data',now_data)
                                    list_shuju.append(now_data)
                                except:
                                    TTime = time.time()
                                    xs = int(time1.split('分钟')[0])
                                    sjc = xs * 60
                                    dp_time = TTime - sjc
                                    now_data = time.strftime('%m月%d日 %H:%M',time.localtime(dp_time))
                                    now_data = now_data[1:]
                                    print('now_data',now_data)
                                    list_shuju.append(now_data)
                            except:
                                if time1[0] == '8':

                                    print('本月发布时间：',time1)
                                    list_shuju.append(time1)
                                elif time1[0] == '昨':
                                    list_shuju.append(time1)
                                else:
                                    print("<<<<<<<<共",num,"条数据<<<<<<<<<<<",keyword,"本月数据读取完毕,写入第",sums,"行,下一用户>>>>>>>>>>>>>>>>>")
                                    self.driver.close()
                                    return sums

                            # 内容.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]//text()
                            content_data = all_li.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]//text()')
                            text = ''
                            for data in content_data:
                                if data == '=':
                                    continue
                                else:
                                    text += data
                            print('内容数据：',text)
                            list_shuju.append(text)


                            # 发布账号主页链接
                            list_shuju.append(home_url)

                            # # 标签
                            # short_pro = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[1]//text()')[0]
                                
                           

                            # # num += 1
                            # print(f'标签：{short_pro}')
                            # # 正文内容
                            # try:
                            #     content_data = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[3]//text()')[0]
                              
                            #     # num+=1
                            #     print('正文内容：',content_data)
                            # except:
                            #     content_data = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[2]//text()')[0]
                            #     print('正文内容：',content_data)

                            # 图片视频链接.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[3]/div[1]//@src

                            # 点赞
                            try:
                                love = all_li.xpath('.//span[@class="gpro0wi8 cwj9ozl2 bzsjyuwj ja2t1vim"]/span/span/text()')[0]
                                # num+=1

                                print('点赞数：',love)
                                list_shuju.append(int(love))
                            except:
                                print('无点赞！',0)
                                list_shuju.append(0)
                            # 分享评论
                            try:
                                comments_data = all_li.xpath('.//div[@class="bp9cbjyn j83agx80 pfnyh3mw p1ueia1e"]/div//span//text()')
                                print('comments_data',comments_data)
                                comm_shu = len(comments_data)
                                print(comm_shu)
                                if comm_shu == 2:
                                    for comm_data in comments_data:
                                        print('comm_data1234',comm_data)
                                        if comm_data[len(comm_data)-1] == '享':
                                            comm_data1 = int(comm_data.split('次')[0])
                                            print('分享数:',comm_data1)
                                            list_shuju.append(comm_data1)

                                        else:
                                            
                                            comm_data1 = int(comm_data.split('条')[0])
                                            print('评论数:',comm_data1)
                                            list_shuju.append(comm_data1)
                                elif comm_shu == 0:
                                    list_shuju.append(0)
                                    list_shuju.append(0)
                                else:
                                    for comm_data in comments_data:
                                        print('comm_data1234',comm_data)
                                        if comm_data[len(comm_data)-1] == '享':
                                            comm_data1 = int(comm_data.split('次')[0])
                                            list_shuju.append(0)
                                            print('评论数:',0)
                                            list_shuju.append(comm_data1)
                                            print('分享数:',comm_data1)

                                        else:

                                            comm_data1 = int(comm_data.split('条')[0])
                                            list_shuju.append(comm_data1)
                                            print('评论数:',comm_data1)   
                                            list_shuju.append(0)
                                            print('分享数:',0)                    
                            except:
                                print('分享评论有误！')
                                continue
                            print('+++list_shuju+++',list_shuju)
                            row = 'A' + str(sums)
                            wsheet1.write_row(row, list_shuju)
                            print('--------------第',num+1,'条数据！--------------------')
                            print('--------------写入到第',sums,'行数据！--------------------')
                            num+=1
                            sums +=1
                
                else:
                    da_list = all_list[:-3]
                    for all_list in da_list[num:len(da_list)+1]:
                        # 临时储存数据的列表
                        list_shuju = []
                        # # 获取网页源码
                        # # 让时间元素出现在页面上
                        # # 将滚动条移动到页面的指定位置
                        # url3 = self.driver.find_element_by_xpath(
                        #     f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{num+1}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')

                        # ActionChains(self.driver).move_to_element(url3).perform()
                        # html = etree.HTML(self.driver.page_source)


                        # url4 = html.xpath(
                        #     f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a//@href')
                        # print('url4555555555555555',url4)


                        text = all_list.xpath(
                            './/div[@class="lzcic4wl"]//text()')

                        # # 贴子链接
                        # # //div[@data-pagelet="ProfileTimeline"]/div[1]//div[@class="j83agx80 cbu4d94t ew0dbk1b irj2b8pg"]/div[2]//@href
                        # try:
                        #     lianjie = all_list.xpath('.//div[@class="buofh1pr"]/div/div[2]//@href')[0]
                        #     print('帖子链接',lianjie)
                        # except:
                        #     print('全文本！')

                        # 账号昵称 //div[@class="qzhwtbm6 knvmm38d"]/span/h2/span/a/strong/span/text()
                        try:
                            zhnc = all_list.xpath(
                                './/div[@class="qzhwtbm6 knvmm38d"]/span/h2/span/a/strong/span/text()')[0]
                            print(f'发布帐号昵称:{zhnc}')
                            list_shuju.append(zhnc)
                        except:
                            print(f'发布帐号昵称:{zhnc}')
                            list_shuju.append(zhnc)

                        # 发布账号id
                        print('发布账号id',keyword)
                        list_shuju.append(keyword)
                                  

                        # 发布时间//div[@class="buofh1pr"]/div/div[2]/span/span/span[2]//text()
                        Time_list = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div/div/div[2]//div[@class="buofh1pr"]/div/div[2]/span/span/span[2]//text()')
                        time1 = ''
                        for Time in Time_list:
                            if Time == '=':
                                continue
                            else:
                                time1 += Time
                        print(time1)
                        try:
                            try:
                                # 1小时转年月日
                                TTime = time.time()
                                xs = int(time1.split('小时')[0])
                                sjc = xs * 60 * 60
                                dp_time = TTime - sjc
                                now_data = time.strftime('%m月%d日 %H:%M',time.localtime(dp_time))
                                now_data = now_data[1:]
                                print('now_data',now_data)
                                list_shuju.append(now_data)
                            except:
                                TTime = time.time()
                                xs = int(time1.split('分钟')[0])
                                sjc = xs * 60
                                dp_time = TTime - sjc
                                now_data = time.strftime('%m月%d日 %H:%M',time.localtime(dp_time))
                                now_data = now_data[1:]
                                print('now_data',now_data)
                                list_shuju.append(now_data)
                        except:
                            if time1[0] == '8':

                                print('本月发布时间：',time1)
                                list_shuju.append(time1)
                            elif time1[0] == '昨':
                                list_shuju.append(time1)
                            else:
                                print("<<<<<<<<共",num,"条数据<<<<<<<<<<<",keyword,"本月数据读取完毕,写入第",sums,"行,下一用户>>>>>>>>>>>>>>>>>")
                                self.driver.close()
                                return sums

                        # 内容.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]//text()
                        content_data = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]//text()')
                        text = ''
                        for data in content_data:
                            if data == '=':
                                continue
                            else:
                                text += data
                        print('内容数据：',text)
                        list_shuju.append(text)


                        # 发布账号主页链接
                        list_shuju.append(home_url)

                        # # 标签
                        # short_pro = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[1]//text()')[0]
                            
                       

                        # # num += 1
                        # print(f'标签：{short_pro}')
                        # # 正文内容
                        # try:
                        #     content_data = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[3]//text()')[0]
                          
                        #     # num+=1
                        #     print('正文内容：',content_data)
                        # except:
                        #     content_data = all_list.xpath('.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[2]//text()')[0]
                        #     print('正文内容：',content_data)

                        # 图片视频链接.//div[@class="rq0escxv l9j0dhe7 du4w35lb hybvsw6c io0zqebd m5lcvass fbipl8qg nwvqtn77 k4urcfbm ni8dbmo4 stjgntxs sbcfpzgs"]/div/div[2]/div/div[3]/div[3]/div[1]//@src

                        # 点赞
                        try:
                            love = all_list.xpath(".//span[@class='gpro0wi8 cwj9ozl2 bzsjyuwj ja2t1vim']/span/span/text()")[0]
                            # num+=1

                            print('点赞数：',love)
                            list_shuju.append(int(love))
                        except:
                            print('无点赞！',0)
                            list_shuju.append(0)
                        # 分享评论
                        try:
                            comments_data = all_list.xpath('.//div[@class="bp9cbjyn j83agx80 pfnyh3mw p1ueia1e"]/div//span//text()')
                            print('comments_data',comments_data)
                            comm_shu = len(comments_data)
                            print(comm_shu)
                            if comm_shu == 2:
                                for comm_data in comments_data:
                                    print('comm_data1234',comm_data)
                                    if comm_data[len(comm_data)-1] == '享':
                                        comm_data1 = int(comm_data.split('次')[0])
                                        print('分享数:',comm_data1)
                                        list_shuju.append(comm_data1)

                                    else:
                                        
                                        comm_data1 = int(comm_data.split('条')[0])
                                        print('评论数:',comm_data1)
                                        list_shuju.append(comm_data1)
                            elif comm_shu == 0:
                                list_shuju.append(0)
                                list_shuju.append(0)
                            else:
                                for comm_data in comments_data:
                                    print('comm_data1234',comm_data)
                                    if comm_data[len(comm_data)-1] == '享':
                                        comm_data1 = int(comm_data.split('次')[0])
                                        list_shuju.append(0)
                                        print('评论数:',0)
                                        list_shuju.append(comm_data1)
                                        print('分享数:',comm_data1)

                                    else:

                                        comm_data1 = int(comm_data.split('条')[0])
                                        list_shuju.append(comm_data1)
                                        print('评论数:',comm_data1)
                                        list_shuju.append(0)
                                        print('分享数:',0)                       
                        except:
                            print('分享评论有误！')
                            continue
                        print('+++list_shuju+++',list_shuju)
                        row = 'A' + str(sums)
                        wsheet1.write_row(row, list_shuju)
                        print('--------------第',num+1,'条数据！--------------------')
                        print('--------------写入到第',sums,'行数据！--------------------')
                        num+=1
                        sums +=1
            except:
                print('提取有误！')
                break

if __name__ == '__main__':
    # 美大地区孔院院长自媒体脸书数据8月
    # keyword_list=['','','','','','','','','','','','','','','','','']
    # keyword_list=['ana.qiao', 'jun.du.334491', 'renyan.li.18', 'dong.hongle.9', 'sofia.mazheng', 'xiaofen.bi.7', 'zheng.fu.1213', 'humanhairextesion', 'UBA.Confucio', 'confucio.ufrgs', 'profile.php?id=100015822002088', 'CIAUCKLAND?__tn__=%2Cd%2CP-R&eid=ARDCG43dUTqfqXZqmYHR89HXZcqa2znznIS_sx6ZM42Z230XY4p8uGDolSQRZrktnGrFvwTyhZJeOKFI', 'ConfuciusInstituteWellington', 'UNSWCI', 'uonconfucius?ref=search&__tn__=%2Cd%2CP-R&eid=ARBgizLv2VBU7mRs0cdC9DsqVXDxgVuk8dytHCUX7F_oFdO6fixTkmcAxN9RhrdCAro1E81BaJVnDh9t']
    # 师资处--欧洲教师自愿者脸书数据8月
    # keyword_list=['daniela.marieiragii.9', 'donna.rice.3511', 'echo.guo.334', 'graceweihair', 'hahahoho2299', 'jessica.chu.982292', 'linlin.jubujubu', 'mjeanas', 'ping.cui.5876', 'ppanan.liu', 'Rebecca.Niu.505', 'suku.bee', 'sunny.qiao.50', 'yang.mi.7758', 'yanli.ren.9', 'profile.php?id=100014285328747', 'celine.jiang.10', 'judyyye.lyu.3', 'jane.chinese.1', 'jing.pan.79', 'jinxiu.wang.754', 'liping.liu.370', 'min.fan.9', 'profile.php?id=100022188851437', 'profile.php?id=100029100170030', 'xiangyi.tanglan', 'li.guodong.50', 'geng.lu.92', 'han.qi.102', 'stefano.shi.509', 'ZhuGuizhi', 'yuge.fu', 'hongmei.wu.54', 'weizheng.soon.16', 'profile.php?id=100035897914640', 'lanyu.huang.12', 'laura.zhang.982', 'peng.fu.372019', 'feifei.guo.399', 'guoli.mei.79', 'eva.zhao.944', 'qian.yin.7921', 'xiaozheng.wang.860416', 'ziqiao.zang', 'profile.php?id=100038229193352', 'anna.xu.940', 'baoyinhui', 'profile.php?id=100013521249592', 'cari.wu.1', 'chang.yan.180', 'profile.php?id=100050102823462', 'chaobing.sun', 'profile.php?id=100024799081166', 'cristina.kachelovevlns', 'profile.php?id=100000264646084', 'duo.wang.737', 'zoe.lou.9231', 'guanyu.you.965', 'hanchun.wan', 'hong.liu.906', 'ivvvyhuang', 'jane.luo.902', 'augusto.zhao', 'jingzhou.wang', 'joanne.deng.77', 'profile.php?id=100010210837474', 'happychhuan', 'jujumeis', 'profile.php?id=100050342435850', 'limei.wang.75873708', 'profile.php?id=100010573636177', 'luna.jin.165', 'maggie.man.359', 'maoyu.sun', 'profile.php?id=100009900046331', 'profile.php?id=100052760522845', 'mike.top.3766', 'profile.php?id=100009729554110', 'profile.php?id=100001713489629', 'zetaminus', 'qizhou.chen.737', 'profile.php?id=100009541824519', 'sandy.huang.33886', 'shi.jiani.77', 'shirley.shi.16', 'shuhua.yin.71', 'shuo.wang.10236', 'song.shuang.927', 'suzy.wang.5872', 'profile.php?id=100004822383793', 'profile.php?id=100001637300025', 'wang.chao.353803', 'weichang.yu.104', 'xinge.zou.7', 'k1395410', 'aberdeen.ci', 'profile.php?id=100045217980706', 'xuyang.jiang', 'yangping.yangping.94', 'profile.php?id=100002055568754', 'yanyan.li.100483', 'profile.php?id=100020292582747', 'yingz.zhao.16', 'yiyun.li.14', 'profile.php?id=100009712898252', 'peng.yuping', 'yunfei.liang.16', 'profile.php?id=100004328221733', 'profile.php?id=100048763005166', 'zheng.wang.50115', 'zhiqing.guo.9678', 'zixun', 'profile.php?id=100051043575325']
    # keyword_list=['daniela.marieiragii.9','suku.bee','yang.mi.7758','linlin.jubujubu','mjeanas','profile.php?id=100029100170030','echo.guo.334','jessica.chu.982292','graceweihair','liping.liu.370','min.fan.9','ppanan.liu','profile.php?id=100014285328747','celine.jiang.10']
    # 亚非处--中方院长个人自媒体脸书数据8月
    # keyword_list=['tsogzolmaa.erdenebayar', 'rangsri.yang', 'miyya.zhang.5', 'yongkang.wang.184']
    # 师资处--亚非（公派途径）脸书数据8月
    #keyword_list=['profile.php?id=100004607378501', 'profile.php?id=100007066143774', 'profile.php?id=100038107328752']
    # 师资处--亚非（发声途径）脸书数据8月
    # keyword_list=['yang.jin.50309', 'rob.mar.71653', 'xu.ma.315', 'jiannisjiang', 'confuciusbuu', 'vanessa.chen.58760', 'tao.feng.948494', 'feifei.dai.1', 'shenghua.zhang.16', 'qingyi.chen.7', 'gongcuiyun.megan']
    # 师资处--美大教师自媒体脸书数据8月
    # keyword_list=['profile.php?id=100021893284838','profile.php?id=100003131589983','profile.php?id=4946315','profile.php?id=100003391386920']
    # keyword_list=['lina.zhang.737001', 'lindawang3112', 'ChinaDoll4ever', 'SpooKPryme', 'mei.hu.5', 'ping.wang.1800', 'helen.lee.796774', 'zhili.chen.50', 'cheermyself3', 'xiao.hu.37853', 'victoria.yl.1', 'maureen.magiera', 'fabianaxm']
    # 欧洲媒体
    # keyword_list=['uclm.es', 'bsuby', 'ikopole', 'instytutkonfucjusza', 'IstitutoConfucioDiMilano', 'icpp.fr', 'KonfuziusInstitutNuernbergErlangen', 'clasaconfucius.ovidius', 'InstitutoConfucioUMinho', 'ConfuciusInstituteMunich', 'KonfucijevInstitut.UNIZG',  'ConfuciusInstituteUBB', 'confuciusmaastricht', 'confuciusinstitute.galway', 'KonfuziusInstitutErfurt', 'kiunibl.org', 'IstitutoConfucioUnimc', 'konfuziusinstitutleipzig', 'civspu', 'ICdeLaReunion', 'BrookesConfuciusInstitute', 'konfucjuszUG', 'chinainmiskolc', 'InstitutConfuciusFinistere', 'InstitutoConfucioUC', 'www.ciut.edu.al', 'Instytut-Konfucjusza-UAM-w-Poznaniu-271081649596487', 'IstitutoConfuciodiRoma', 'konfuziusinstitut', 'CIatGlasgowUni', 'profile.php?id=100009360645905', 'pecsikonfuciuszintezet', 'ConfuciusMCR', 'Vilniaus.universiteto.Konfucijaus.institutas', 'IC.ULPGC', 'institutconfuciusmontpellier', 'confucioule', 'IstitutoConfucioUCSC', 'ConfucioUniTo', 'IstitutoConfuciodiPisa', 'bangorconfuciusinstitute', 'BCIUL', 'InstitutConfuciusdesPaysdelaLoire', 'KonfuciuvInstitut', 'konfucius.vsfs', 'KonfuziusInstitutFrankfurt', 'profile.php?id=100057530954564', 'Institut-Confucius-de-Bretagne-127321330622202', 'Школа-Конфуций-346940955894652', 'InstitutoConfucio.UP', 'confuciusinstituteaberdeen', 'Groningen-Confucius-Institute-108520622564327', 'institutulconfuciusbucuresti', 'NEOMACONFUCIUSINSTITUTEFORBUSINESS', 'institutkonfucij.mk', 'Institut-Confucius-de-Liège-154641651216924', 'ConfuciusCovUni', 'um.confucius', 'confucius.instituteucc.1', 'IstitutoConfucioUnipd', 'Confucioenna', 'istituto.confucio.napoli', 'Konfuciov-In%C5%A1tit%C3%BAt-v-Bratislave-1699960763610272', 'Konfuzius-Institut-an-der-Universit%C3%A4t-Freiburg-eV-641341015921819', 'szegedikonfuciuszintezet']
    # 亚非处--官方网站脸书数据8月
    # keyword_list=['confucius.ainshams/', 'pjkyhyst', 'kenyattaconfucius/?eid=ARDA_cozhP8f8J7PivzHdYxH1BrXIdGnNX_oGgDNQ5VTTcXYV--qMb-dzqXDvPGygj5UthscMz3OKjvj&timeline_context_item_type=intro_card_education&timeline_context_item_source=100033838542166&fref=tag', 'cinsubd/?__tn__=%2Cd%2CP-R&eid=ARBaELSZvuqq2d7Z2AJbsr1a4udB83RPhSJeJv7hC2q2NtVXGw6i96PkqFNAu7McSi9PhrH_xjU6N0wD', 'haishangsilu/', 'umpmlcc', 'cisdus.suphanburi', 'Mandarim-na-CV-319869092135514/', 'UJCI1/', 'cscc66/', 'Confucius-PSU-Hatyai-637584140021699/', 'ConfuciusInstituteSU/?__tn__=%2Cd-%5C-R&eid=ARCI3qkwjodl5IAOUYY-mM1q4t-C45qEIbBUjdD8iPhtDdnLFvO7olagu4sakPfQlhUfzfMZ2dDWClaW', 'confuciusudsm/?__tn__=%2Cd%2CP-R&eid=ARDJggd4XDXqzzfMTmHTLB1afYiEhwb8jXNgj9Z80a3LpzlBrlLrHnG7Ihd_oQt5AY0vVNT44JTqipGb', 'AUFconfucius/', 'KZIUM/', 'yguinternationalcenter/?__tn__=%2Cd%2CP-R&eid=ARBMc5h6kj6s5TUqQYTvi1H5sXCzbjkgi9EUlC5DwKpCN-eKqMIuv0X-_35EhI6vFwdrQTV5P_wKQkEY', 'TMCKZKT2006/', 'uob.institutconfucius', 'ciub.botswana.9', 'ConfuciusUniversityofNairobi/?__tn__=%2Cd%2CP-R&eid=ARAn05_8u1wFIgok3127lQg4l7vQPbbUHrKgE0i4LnJhr7xbfoAglKmXYpG5stBsKIvi3rsJdEXzCs1K', 'www.uae.ma/', 'ateneoconfucius/?ref=br_rs', 'CIUOC/', 'TAGConfucius/', 'Institut-Confucius-de-lAcad%C3%A9mie-Diplomatique-Congolaise-100658168167864/', 'Confucius-Institute-at-the-University-of-the-Philippines-563785900626348/', 'CIRAC.edu/', '%E0%BA%AA%E0%BA%B0%E0%BA%96%E0%BA%B2%E0%BA%9A%E0%BA%B1%E0%BA%99%E0%BA%82%E0%BA%BB%E0%BA%87%E0%BA%88%E0%BA%B7-%E0%BA%A1%E0%BA%8A-538306683255260/?__tn__=%2Cd%2CP-R&eid=ARDue1VjE-JNr-BI59WFNFZEGI98QZ6w2eROHK7wAEezRyQwa9_ZlUixj7VnE-i4-VKB9aThhnAmyuth', 'Segiconfucius/', 'wdkyCHN/', 'CI.Assumption/?__tn__=%2Cd%2CP-R&eid=ARCAlblYZvxv0yhgz57IF-_bjBF0z21I0WynB44K5lFL1l2d7dIPwZTpfNhmvFhSOtHFdTN5Smfm3DZ7', 'kungzitau/', 'pusatterjemahalazhar/']
    # 志愿者处脸书数据8月
    # keyword_list=['LowProfileLuxurious', 'lu.hong.94214', 'cheng.kim.311', 'tan.jue.35', '100029205681446', 'lucy.luan.319', 'louis.wang.921', 'MR.yaoyang', 'chao.yang.3958', 'claire.zhao.902', 'liu.h.hui.73', 'huafang.shen', 'lingling.he.14', 'hai.chang.31', 'ricki.lei.9', 'fei.sun.731135', 'htetnaing.htun.522', 'sebastian.paguyan', 'JooliaWang', 'cheli.sag', 'wiley.lee.7', 'xia.han.9', 'wenxuan.zuo.73', 'tarquin.wang', 'zoe.wang1', 'YAQIYQ', '100006981612725', 'Fionawu3698', 'gloriatzen', 'sophia.wu.50767984', 'woo520123', 'xia.chang.9237', 'xinling.wang.39395']
    # 补充数据
    # keyword_list=['kunthea.yan.10','Fuyu-187988891256633','100023579753735','monica.ch.5811']
    keyword_list = [ 'suku.bee']
    # 写入excel
    try:
        wbook = xlsxwriter.Workbook('suku.bee.xlsx')
        # wbook = xlsxwriter.Workbook('师资处--欧洲教师自愿者脸书数据8月.xlsx')
        # 创建工作表
        wsheet1 = wbook.add_worksheet('Sheet1')
        title = ['发布账号昵称','发布账号ID','发布时间','内容','账号主页链接','点赞数','评论数','分享数']
        wsheet1.write_row('A1',title) #从A1单元格写入表头
        # excel 所有用户总发帖数
        zong_sums = 2
        for keyword in keyword_list:
            fb_server = FB()
            zong_sums = fb_server.start(keyword,zong_sums,wsheet1)
            sleep(random.randint(15 , 30))
            print('写入完成！',zong_sums)
        wbook.close()

    except:
        wbook.close()
        print("人工终止！")