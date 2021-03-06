# -*- coding: utf-8 -*-
'''
Created on Jun 30, 2015

@author: lin
'''
import requests
import eventlet
import json
import time
import client
import proxy
from exception import *
eventlet.monkey_patch()

class Request(object):
    
    def __init__(self):
        self.client = client.Client()
        self.proxy = proxy.Proxy()
        self.t = time.time()
        self.client_id = self.client.nextClientId()
        self.proxy_address = self.proxy.nextProxy()
    
    def query_videos_by_catetory(self, page = 1, count = 1, 
                    url = 'https://openapi.youku.com/v2/videos/by_category.json',
                    period = 'history', 
                    category = None, genre = None,
                    orderby = 'comment-count',
                    ):
        params = {}
        params['client_id'] = self.client_id
        if category is not None:
            params['category'] = category
        if genre is not None:
            params['genre'] = genre
        params['period'] = period
        params['orderby'] = orderby
        params['page'] = page
        params['count'] = count
        
        return self.get_data(params, url)

    def query_comments_by_video(self,
                                video_id = None,
                                page = None,
                                count = None,
                                url = 'https://openapi.youku.com/v2/comments/by_video.json'):
        params = {}
        params['client_id'] = self.client_id
        params['video_id'] = video_id
        params['page'] = page
        params['count'] = count

        return self.get_data(params, url)
       

    
    def query_favor_videos_by_user(self,
                                   user_id = None,
                                   page = 1,
                                   count = 1,
                                   url = 'https://openapi.youku.com/v2/videos/favorite/by_user.json'
                                   ):
        params = {}
        params['page'] = 1
        params['count'] = 1
#         params[]
        
        return self.get_data(params, url)

    def query_user_by_id(self, client_id = '9c5f810f1c6b0bf0',
                         user_ids = None,
                         url = 'https://openapi.youku.com/v2/users/show_batch.json'
                         ):
        params = {}
        params['client_id'] = client_id
        params['user_ids'] = user_ids
        return self.get_data(params, url)
    
    def query_a_user_by_id(self, client_id = '9c5f810f1c6b0bf0',
                         user_id = None,
                         url = 'https://openapi.youku.com/v2/users/show.json'
                         ):
        params = {}
        params['client_id'] = client_id
        params['user_id'] = user_id
        return self.get_data(params, url)
    
    def get_data(self, params, url):
        r = None
        data = {}
        self.t = time.time()
        params['client_id'] = self.client_id
        count = 0
        while True:
            try:
                with eventlet.Timeout(10):
#                     r = requests.get(url, params=params, proxies = {'https':self.proxy_address, 'http':self.proxy_address})
                    count += 1
                    r = requests.get(url, params = params)
                    #解决返回空行的问题
                    if count == 10:
                        print "over 10 times retries"
                        return {'error':'none'}
                    try:
                        data = json.loads(json.dumps(r.json()))
                    except ValueError as detail:
                        # 有些数据返回之后没法解析,这些数据直接跳过
                        # bad gateway 是其中一个返回
                        print "in ValueError"
                        print detail
                        self.proxy_address = self.proxy.nextProxy()
                        continue
                    if 'error' in data and data['error']['code'] == 1017:
                        # 如果访问频率超过限制,切换client_id
                        self.client_id = self.client.nextClientId()
                        params['client_id'] = self.client_id
                        print 'switching client_id', self.client_id
                        continue
                    return data
                # 如果访问api的响应时间太慢,说明youku开始封锁ip,选择另外一个代理ip
            except (eventlet.timeout.Timeout, requests.exceptions.ProxyError,
                    requests.exceptions.ConnectionError) as detail:
                print "in Timeout"
                print detail
                self.proxy_address = self.proxy.nextProxy()
            except Exception as detail:
#                 except_stop()
                print "after Timeout"
                self.proxy_address = self.proxy.nextProxy()
                print detail
    
if __name__ == '__main__':
    req = Request()
    videoid = 'XMTM3NDcyNTUxMg==';
    page = 0;
    count = 100;
    url = 'https://openapi.youku.com/v2/comments/by_video.json'
    res = req.query_comments_by_video(video_id = videoid, page = page, count = count, url = url)
    print res 
    
         
    
    
    
    
    