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
eventlet.monkey_patch()

class Request(object):
    
    def __init__(self):
        self.client = client.Client()
        self.proxy = proxy.Proxy()
        self.t = time.time()
        self.client_id = self.client.nextClientId()
        self.proxy_address = self.proxy.nextProxy()
    
    def query_videos_by_catetory(page = 1, count = 1, 
                    url = 'https://openapi.youku.com/v2/videos/by_category.json',
                    period = 'history', client_id = 'f0271cccdc9ac157',
                    category = None, genre = None,
                    orderby = 'comment-count',
                    ):
        params = {}
        params['client_id'] = client_id
        if category is not None:
            params['category'] = category
        if genre is not None:
            params['genre'] = genre
        params['period'] = period
        params['orderby'] = orderby
        params['page'] = page
        params['count'] = count
        r = requests.get(url, params=params)
        # 将返货的list类型的数据转换成dict
        data = json.loads(json.dumps(r.json()))
        return data

    def query_comments_by_video(self,
                                video_id = None,
                                page = None,
                                count = None,
                                url = 'https://openapi.youku.com/v2/comments/by_video.json'):
        # ------------------------------------------------------------------------
        params = {}
        params['client_id'] = self.client_id
        params['video_id'] = video_id
        params['page'] = page
        params['count'] = count
        # ------------------------------------------------------------------------

        # ------------------------------------------------------------------------
        r = None
        data = {}
        self.t = time.time()
        try:
            with eventlet.Timeout(10):
                    r = requests.get(url, params=params, proxies = {'https':self.proxy_address, 'http':self.proxy_address},
                                     )
            # 如果访问api的响应时间太慢,说明youku开始封锁ip,选择另外一个代理ip
        except (eventlet.timeout.Timeout, requests.exceptions.ProxyError) as detail:
            self.proxy_address = self.proxy.nextProxy()
            data['ignore'] = '1'
            return data
        
#         except Exception as detail:
#             # 如果在使用proxy过程中出问题,换代理
#             # 返回ignore的data
#             print 'here', detail
#             self.proxy_address = self.proxy.nextProxy()
#             data['ignore'] = '1'
#             print 'return 2'
#             return data

        # ------------------------------------------------------------------------

        # ------------------------------------------------------------------------
        try:
            data = json.loads(json.dumps(r.json()))
        except ValueError as detail:
            # 有些数据返回之后没法解析,这些数据直接跳过
            data['ignore'] = '1'
            print detail

        if 'error' in data and data['error']['code'] == 1017:
            # 如果访问频率超过限制,切换client_id
            self.client_id = self.client.nextClientId()
            print 'switching client_id'
        # ------------------------------------------------------------------------
        print 'return 3' 
        return data
    
    def query_favor_videos_by_user(client_id = '9c5f810f1c6b0bf0',
                                   user_id = None,
                                   page = 1,
                                   count = 1,
                                   url = 'https://openapi.youku.com/v2/comments/by_video.json'
                                   ):
        params = {}
        params['client_id'] = client_id
        if user_id is None:
            print "!!!!!!!!user_id is NOne, in query_favor_videos_by_user"
        else:
    #         params['user_id'] = '10150955269'
            pass
    #     params['user_name'] = '谢耳朵33139961'
    #     params['page'] = page
    #     params['count'] = count
        r = requests.get(url, params = params)
        data = {}
        try:
            data = json.loads(json.dumps(r.json()))
        except ValueError as detail:
            data['error'] = r.text.split(' ')
        return data
    
    def query_user_by_id(client_id = '9c5f810f1c6b0bf0',
                         user_ids = None,
                         url = 'https://openapi.youku.com/v2/comments/by_video.json'
                         ):
        params = {}
        params['client_id'] = client_id
        if user_ids is None:
            print "!!!!1user_ids is None, in query_user_by_id"
        else:
            params['user_ids'] = user_ids
        r = requests.get(url, params = params)
        data = {}
        try:
            data = json.loads(json.dumps(r.json()))
        except ValueError as detail:
            data['error'] = r.text.split(' ')
        return data
    
    
    
    
    
    
    
    