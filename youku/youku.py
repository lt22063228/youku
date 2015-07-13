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

# print type(data)
categories = ['电视剧', '电影', '综艺', '动漫', '音乐', '教育', '纪录片', '资讯', '娱乐', '体育', '汽车', '科技', '游戏', 
              '生活', '时尚', '旅游', '亲子', '搞笑', '微电影', '网剧', '拍客', '创意视频', '自拍', '广告']
def getVideosByCate():
    # logging 配置
    import logging  
    import os

    sess = session.getSession()
    allVideos = session.get_all_videos(sess)
    allUsers = session.get_all_users(sess)
    print 'allUsers print', ('40447279' in allUsers)
    print 'allvideos print', ('XMTI2MDQ0NDYzMg==' in allVideos)
    for cate in categories:
        # 所有参数设置在这
        page = 1
        count = 100
        period = 'today'
        # 结束参数设置
        temp = []
        print 'haha'
        req = Request()
        print 'hehe'
        while True:
            data = req.query_videos_by_catetory(count = count, page = page,
                                            category = cate,
                                            period = period
                                            )
            if 'error' in data and data['error']['code'] != 1017:
                pprint(data)
                break
            videos = data['videos']
            for video in videos:
                temp.append(video)
            session.insert_videos(temp, sess, allVideos, allUsers)
            if len(videos) < 99: break 
            page += 1
    sess.close()
def testGetUserById(userId):
    data = query_user_by_id(user_ids = userId)
    pprint(data)
def testGetFavorsByUser(userId):
    page = 1
    count = 1
    data = query_favor_videos_by_user(user_id = userId, page = page, count = count)
    pprint(data)
def testGetVideos():
    page = 1
    count = 1
    for cate in categories:
        data = query_videos_by_catetory(page = page, count = count, category = cate, period = 'today')
        pprint(data)
def testGetComments(videoId):
    page = 18458
    count = 1
    data = query_comments_by_video(video_id = videoId, count = count, page = page) 
    pprint(data)
def getVideos():
    page = 1200
    total = 0
    # logging 配置
    import logging  
    import os
    logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.DEBUG)  

    sess = session.getSession()
    while True:
        data = query_videos_by_catetory(count = 100, page = page)
        if 'error' in data:
            if data['error']['code'] == 1014:
                logging.debug('error 1014, maximum matching(page*count)')        
            else:
                
                pprint(data)
                logging.debug('error'+data['error']['code'])
            break
        videos = data['videos']
        for video in videos:
            session.insert_video(video, sess)
        page += 1
        print page
    sess.close()

def getCommentsByVideoId(videoId, users, req, sess):
    page = 1
    count = 100

    # logging 配置
    comment_count = 0
    while True:

        data = req.query_comments_by_video(video_id = videoId, count = count, page = page)
#         pprint(data)
        if 'error' in data:
            break
        elif 'ignore' in data:
            page += 1
            continue
        comments = data['comments']
        print 'len of comments', len(comments)
        if len(comments) == 0: break
        if comment_count > 2000: 
            break
        temp = []
        for comment in comments:
            comment_count += 1
            comment['video'] = data['video_id']
            if 'user' not in comment: continue
            temp.append(comment)
        comments = temp
        session.insert_comments(comments, sess, users)
        page += 1
    

def getCommentsForAllVideos():
    sess = session.getSession()
#     session.remove_uncommented_videos(sess)
    videos = session.get_all_videos(sess)
    users = session.get_all_users(sess)
    sess.close()
    commentedVideoIds = getDistinctCommentedVideoIds()
    print 'ha'
    req = Request()
    print 'he'
    sess = session.getSession()
    for video in videos:
        s = time.time()
        if video not in commentedVideoIds:
            getCommentsByVideoId(video, users, req = req, sess = sess)
        f = time.time()
        print 'a video time used is:', f - s
    sess.close()

def getFavorByUser(userId):
    # 这个方法暂时存在问题，发送过去的请求没法很好被解析，总是返回错误
    page = 1
    
        # logging 配置
    import logging  
    import os
    logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.DEBUG)  
    
    sess = session.getSession()
    while True:
        data = query_favor_videos_by_user(user_id = userId)
        if 'error' in data:
            logging.debug('error' + str(data['error']['code']))
            break
        videos = data['videos']
        for video in videos:
            session.insert_favor_by_user(video, userId, sess)
        page += 1
        print page
    print page
    sess.close()
def getDistinctCommentedVideoIds():
    sess = session.getSession()
    res = session.get_all_commented_videos(sess)
    sess.close()
    return res
        
if __name__ == '__main__':
    pass
#     testGetFavorsByUser(userId = '99201492')
#     getCommentsByVideoId('XOTYxNDcyNDA4')
#     testGetComments('XOTYxNDcyNDA4')
#     testGetVideos()
#     getVideos()
#     testGetUserById('99201492,99034753')
    getVideosByCate()
#     getCommentsForAllVideos()
        