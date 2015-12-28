# -*- coding: utf-8 -*-
'''
Created on Jun 29, 2015

@author: lin
'''
import time
from vod_orm import *
import session
from req import *
import requests
import json
from pprint import *
import datetime
import sqlalchemy.exc
import proxy
import client

# 使用带参数的Get请求访问api的url
class Youku():
    def __init__(self):
        self.sess = session.MySession()
        self.req = Request()
        self.categories = ['电视剧', '电影', '综艺', '动漫', '音乐', '教育', '纪录片', '资讯', '娱乐', '体育', '汽车', '科技', '游戏', 
                  '生活', '时尚', '旅游', '亲子', '搞笑', '微电影', '网剧', '拍客', '创意视频', '自拍', '广告']
        self.video_genre = {'电视剧':['古装','武侠','警匪','军事','神话','科幻','悬疑',
                             '历史','儿童','农村','都市','家庭','搞笑',
                             '偶像','言情','时装','优酷出品'],
                      '电影':['武侠','警匪','犯罪','科幻','战争','恐怖','惊悚','纪录片',
                            '西部','戏曲','歌舞','奇幻','冒险','悬疑','历史',
                            '动作','传记','动画','儿童','喜剧','爱情','剧情','运动',
                            '短片','优酷出品'],
                      '综艺':['优酷出品','优酷牛人','脱口秀','真人秀','选秀','美食',
                            '旅游','汽车','访谈','记实','搞笑','时尚','晚会',
                            '理财','演唱会','益智','音乐','舞蹈','体育娱乐','游戏','生活'],
                      '动漫':['热血','格斗','恋爱','美少女','校园','搞笑','LOLI','神魔',
                            '机战','科幻','真人','青春','魔法','神话','冒险','运动',
                            '竞技','童话','亲子','教育','励志','剧情','社会','历史','战争'],
                      }
        self.show_genre = {
                           
                           }
        self.allVideos = self.sess.get_all_videos()
        self.allUsers = self.sess.get_all_users()

    def close(self):
        self.sess.close()
    def getVideosByCate(self):
    
        videoIdSet = set(self.allVideos.keys())
        userIdSet = self.allUsers

        for cate in self.categories:
            # 所有参数设置在这
            page = 1
            count = 100
            period = 'month'
            # 结束参数设置
            temp = []
            while True:
                data = self.req.query_videos_by_catetory(count = count, page = page,
                                                category = cate,
                                                period = period
                                                )
                if 'error' in data and data['error']['code'] != 1017:
                    pprint(data)
                    break
                videos = data['videos']
                for video in videos:
                    temp.append(video)
                self.sess.insert_videos(videos = temp, videoIdSet = videoIdSet, userIdSet = userIdSet)
                if len(videos) < 99: break 
                page += 1

    def testGetUserById(self,userId):
        data = self.req.query_user_by_id(user_ids = userId)
        pprint(data)
    def testGetFavorsByUser(self,userId):
        page = 1
        count = 1
        data = self.req.query_favor_videos_by_user(user_id = userId, page = page, count = count)
        pprint(data)
    def testGetVideos(self):
        page = 1
        count = 1
        for cate in self.categories:
            data = self.req.query_videos_by_catetory(page = page, count = count, category = cate, period = 'today')
            pprint(data)
    def testGetComments(self,videoId):
        page = 18458
        count = 1
        data = self.query_comments_by_video(video_id = videoId, count = count, page = page) 
        pprint(data)
    
    def getCommentsByVideoId(self, videoId, page = None):
        page = 1 if page is None else page
        count = 100
    
        # logging 配置
        comment_count = 0
        while True:
            data = self.req.query_comments_by_video(video_id = videoId, count = count, page = page)
            if 'error' in data:
                break
            elif 'ignore' in data:
                page += 1
                continue
            comments = data['comments']
            print 'len of comments', len(comments)
            if len(comments) == 0: break
            temp = []
            for comment in comments:
                comment_count += 1
                comment['video'] = data['video_id']
                if 'user' not in comment: continue
                temp.append(comment)
            comments = temp
            self.sess.insert_comments(comments, self.allUsers)
            page += 1
        
    def updateUser(self):
        count = 0; ids = ""; all_count = 0
        maxid = self.sess.get_max_active_user_id()[0]
        print maxid
        uninfo_users = self.sess.get_seq_users(maxid)
 
        for idx, user in enumerate(uninfo_users):
            if count == 100 or idx == len(uninfo_users)-1:
                data = self.req.query_user_by_id(user_ids = ids[1:])
                if 'ignore' in data: 
                    print 'ignore'
                    continue
                if 'users' not in data:
                    print data; break
                us = data['users']
                if len(us) != 0: all_count += self.sess.update_users(us)
                ids = ''; count = 0
                if len(us) == 0: continue
            ids += ',' + user
            if all_count % 1000 < 100: print "all_count", all_count
            count += 1
        print 'update finish'
                
    def getCommentsForAllVideos(self):
        commentedVideoIds = self.getDistinctCommentedVideoIds()
        print 'start'
        for video in self.allVideos:
            s = time.time()
            if video not in commentedVideoIds:
                self.getCommentsByVideoId(video, page = self.allVideos[video] / 100 + 1)
            f = time.time()
            print 'a video time used is:', f - s
    
    def getFavorByUser(self, userId):
        # 这个方法暂时存在问题，发送过去的请求没法很好被解析，总是返回错误
        page = 1
        while True:
            data = self.req.query_favor_videos_by_user(user_id = userId)
            if 'error' in data:
                print data
            videos = data['videos']
            for video in videos:
                sess.insert_favor_by_user(video, userId)
            page += 1
            print page
    def getDistinctCommentedVideoIds(self):
        res = self.sess.get_all_commented_videos()
        return res
            
if __name__ == '__main__':
    youku = Youku()
#     youku.getVideosByCate()
    youku.updateUser()
#     youku.getCommentsForAllVideos()
#     youku.getCommentsForAllVideos()
    youku.close()
#     testGetFavorsByUser(userId = '99201492')
#     getCommentsByVideoId('XOTYxNDcyNDA4')
#     testGetComments('XOTYxNDcyNDA4')
#     testGetVideos()
#     getVideos()
#     testGetUserById('99201492,99034753')
#     getVideosByCate()
#     getCommentsForAllVideos()
        