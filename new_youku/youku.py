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
                       '资讯':['社会资讯','科技资讯','生活资讯','时政资讯','军事资讯','财经资讯','法制'],
                       '娱乐':['娱乐资讯','电视资讯','电影资讯','音乐资讯','颁奖礼','戏剧','曲艺','艺术','魔术'],
                       '体育':['世界杯','体育资讯','篮球','CBA','足球','英超','极限运动','跑酷','自行车','轮滑','滑板','武术','格斗','赛车','大球运动',
                             '小球运动','网球','田径','水上项目','力量项目','冰雪项目','射击','健身','体育舞蹈','技巧','棋牌','模型','其他','奥运会','欧洲杯'
                             ],
                        '汽车':['车讯','购车','试驾','新车','国产车','欧洲','美国','日韩','其他地区','宝马','通用','丰田','福特','大众',
                              '戴勒姆-克莱斯勒','现代-起亚','日产','标致-雪铁龙','本田','雷诺','养车','修车','改装','装饰','赛车','二手车','名车','车女郎','车广告','学车',
                              '飙车','车友会','摩托车','F1'
                              ],
                        '科技':['数码','App','游戏机','GPS','数字家电','MP3/MP4','DC/DV','笔记本','手机','IT','平板'],
                        '游戏':['游戏资讯','网络游戏','游戏音乐','电子竞技','单机游戏','魔兽世界','地下城与勇士','手机游戏'],
                        '生活':['休闲','潮品','婚恋','女性','家居','健康','居家','宠物','聚会','美食','记录'],
                        '时尚':['美容','修身','服装服饰','时尚购物','潮人','情感星座'],
                        '旅游':['城市','户外运动','节庆活动','自然景点','人文景点','游轮岛屿','乡村古镇','旅游用品','交通住宿','旅游业界','出境游','国内游','攻略指南'],
                        '亲子':['育儿','宝宝秀','妈妈','早教','怀孕','搞笑儿童'],
                        '搞笑':['恶搞短片','搞笑自拍','搞笑动物'],
                        '微电影':[],
                        '网剧':[],
                        '拍客':[],
                        '创意视频':[],
                        '自拍':[],
                        '广告':[]
                      }
        self.show_genre = {
                           '音乐':['音乐MV', '现场版', '演唱会', '电影原声', '电视剧原声', '动漫音乐', '游戏音乐', '广告音乐'],
                           '教育':['公开课', '名人名嘴', '文化', '艺术', '伦理社会','理工','历史','心理学','经济','政治','管理学','外语','法律','计算机','哲学','职业培训','家庭教育'],
                           '纪录片':['人物','军事','历史','自然','古迹','探险','科技','文化','刑侦','社会','旅游'],
                           }
        self.show_genre = {
                           
                           }
        print '1'
        self.allVideos = self.sess.get_all_videos()
        print '2'
        self.allUsers = self.sess.get_all_users()
        print '3'

    def close(self):
        self.sess.close()
        
    def getPopVideos(self, cate = None):
        """
            get popular videos
        """

        videoIdSet = set(self.allVideos.keys())
        userIdSet = self.allUsers
        
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
#                 pprint(data)
                break

            videos = data['videos']
            for video in videos:
                temp.append(video)
            self.sess.insert_videos(videos = temp, videoIdSet = videoIdSet, userIdSet = userIdSet)
            if len(videos) < 99: break 
            page += 1

    def getVideosByCate(self):
    
        videoIdSet = set(self.allVideos.keys())
        userIdSet = self.allUsers

        for cate in self.categories:
            self.getPopVideos(cate = cate)
############################################
### start of test method.
############################################
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
############################################
### end of test method.
############################################
    
    def getCommentsByVideoId(self, videoId, page = None):
        page = 1 if page is None else page
        count = 100
    
        comment_count = 0
        while True:
            # get comments associating with videoId, starting at page=page.
            data = self.req.query_comments_by_video(video_id = videoId, count = count, page = page)
            if 'error' in data:
                break
            elif 'ignore' in data:
                page += 1
                continue
            comments = data['comments']
            print 'len of comments', len(comments)

            # if the length of comments list is 0, no comments data get, break.
            if len(comments) == 0: break
            
            # add 100 comments to the database.
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

    def getDistinctCommentedVideoIds(self):
        res = self.sess.get_all_commented_videos()
        return res

            
if __name__ == '__main__':
    print 'hehe'
    youku = Youku()
    youku.getCommentsForAllVideos()
    youku.close()
        