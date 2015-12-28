# -*- coding: utf-8 -*-
'''
Created on Jun 29, 2015

@author: lin
'''
from vod_orm import *
import sqlalchemy.exc
from sqlalchemy.sql.expression import *
class MySession():
    def __init__(self):
        self.session = self.getSession()
    def close(self):
        self.session.close()

    def getSession(self):
    
        from sqlalchemy import create_engine
        
        engine = create_engine('mysql://root:123456@localhost:3306/vod?charset=utf8', encoding='utf-8', echo=False)
        
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def insert_video(self, video):
        '''
            video是api返回的视频信息，是以dict的形式存储的
            如果数据库中已经存在这个video，更新数据
            video中包含信息uploader，往user表中插入这个用户，
            如果已经包含了，跳过
        '''
        v = Video(id = video['id'], title = video['title'], 
                  link = video['link'], duration = video['duration'],
                  category = video['category'], view_count = video['view_count'],
                  favorite_count = video['favorite_count'], comment_count = video['comment_count'],
                  up_count = video['up_count'], down_count = video['down_count'],
                  published = video['published'], user = video['user']['id'],
                  )
        u = User(id = v.user)
        # 先出入uploader的用户数据
        try:
            # 此时用户表中的数据只有一个id字段
            session.add(u)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            # 已经存在这个用户，直接跳过插入
            session.rollback()
        try:
            session.add(v)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            # 已经存在这个视频，更新视频信息
            session.rollback()
            originVideo = session.query(Video).filter(Video.id == video['id']).one()
            originVideo.copy(v)
            session.commit()
            
    def insert_videos(self, videos, videoIdSet, userIdSet):
    
        userList = []
        videoList = []    
        updateList = []
        for video in videos:
            
            v = Video(id = video['id'], title = video['title'], 
                          link = video['link'], duration = video['duration'],
                          category = video['category'], view_count = video['view_count'],
                          favorite_count = video['favorite_count'], comment_count = video['comment_count'],
                          up_count = video['up_count'], down_count = video['down_count'],
                          published = video['published'], user = video['user']['id'],
                          )
            u = User(id = v.user)
            
            if str(u.id) not in userIdSet:
                userList.append(u)
                userIdSet.add(str(u.id))
            if str(v.id) not in videoIdSet:
#                 print str(v.id), type(str(v.id)), '.......'
#                 if str(v.id) == 'XMTI4MzQ3MDQ5Mg==':
#                     print 'haha'
                if v.comment_count > 99:
                    videoList.append(v)
                    videoIdSet.add(str(v.id))
            else:
                updateList.append(v)
    
        for each in userList: self.session.add(each)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            print detail
            self.session.rollback()
        
        for each in updateList:
            try:
                originVideo = self.session.query(Video).filter(Video.id == video['id']).one()
            except sqlalchemy.orm.exc.NoResultFound as detail:
                # 说明不需要更新,因为也是在这轮查询中才插入的
                continue
            originVideo.copy(v)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            print detail
            self.session.rollback()
        
        print 'len of videos', len(videoList)
        for each in videoList: self.session.add(each) 
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            print detail
            self.session.rollback()
    
            
            
    def insert_comments(self, comments, users):
        '''
            insert_comment 的多个插入版本
            每次获取的comments的数量是100,对于每个comment,获取其users集合
            对于已经存在的user,过滤掉
            如果存在已经存在的comment,直接放弃这100个comments,转向下一个100comments的获取
            这样做可以让comment每一百提交一次
        '''
        userList = []
        commentList = []
        for comment in comments:
    
            c = Comment(id = comment['id'], user = comment['user']['id'],
                        video = comment['video'], content = comment['content'],
                        published = comment['published']
                        )
    
            if str(comment['user']['id']) not in users: 
                u = User(id = c.user)
                userList.append(u)
    
                users.add(str(comment['user']['id']))
            else:
                pass
            commentList.append(c)
        for each in userList: self.session.add(each)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            # 一定是已经存在comment, 直接放弃
            print detail
            self.session.rollback()
    
        for each in commentList: self.session.add(each)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            # 一定是已经存在comment, 直接放弃
            print detail
            print 'abort 100'
            self.session.rollback()
    
    
    def insert_favor_by_user(self, video, userId):
        '''
            video : dict
            userId : string
            session : sqlalchemy 中的对象
            根据用户寻找到用户收藏的视频，将（用户，视频）对插入favor关系表中，如果视频中
            还不存在这个视频，则插入该视频 
        '''
        v = Video(id = video['id'], title = video['title'], 
                  link = video['link'], duration = video['duration'],
                  category = video['category'], view_count = video['view_count'],
                  favorite_count = video['favorite_count'], comment_count = video['comment_count'],
                  up_count = video['up_count'], down_count = video['down_count'],
                  published = video['published'], user = video['user']['id'],
                  )
        
        try:
            self.session.add(v)
        except sqlalchemy.exc.IntegrityError:
            self.session.commit()
            # 用户收藏的视频已经在数据库中存在，因此就秩序更新视频信息
            self.session.rollback()
            originVideo = self.session.query(Video).filter(Video.id == video['id']).one()
            originVideo.copy(v)
            self.session.commit()
            
        favor = Favor(id = (video.id + '#' + userId), video = video.id, user = userId)
        try:
            self.session.add(favor)
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            # 收藏关系已经存在数据库中，为什么会这样。。。可能多次运行程序了，
            # 会试图获取同一个用户的收藏视频信息
            # 直接跳过
            self.session.rollback()
    def update_users(self, users):
        user_list = []
        count = 0
        for each in users:
            u = ActiveUser(id = each['id'], name = each['name'], link = each['link'], 
                     gender = each['gender'], description = each['description'], videos_count = each['videos_count'],
                     playlist_count = each['playlists_count'], favorites_count = each['favorites_count'],
                     followers_count = each['followers_count'], following_count = each['following_count'],
                     statuses_count = each['statuses_count'], vv_count = each['vv_count'],
                     regist_time = each['regist_time'])
            if u.vv_count > 50:
                user_list.append(u)
                count += 1
#             try:
#                 originUser = self.session.query(User).filter(User.id == each['id']).one()
#             except sqlalchemy.orm.exc.NoResultFound as detail:
#                 print 'session line:207.'
#                 break
#             originUser.copy(u)
        for each in user_list: self.session.add(each)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            print detail
            self.session.rollback()
        return count
     
    def get_all_videos(self):
        dict1 = { x[0]:0 for x in self.session.query(Video.id).all()}
        dict2 = {x[0]:x[1] for x in self.session.query(Comment.video, func.count(Comment.video)).group_by(Comment.video).all()}
        for d1 in dict1:
            if d1 not in dict2:
                dict2[d1] = dict1[d1]
        return dict2
    
    def get_all_users(self):
        res = self.session.query(User.id).all()
        return set([x[0] for x in res])
    
    def get_seq_users(self, maxid):
        res = self.session.query(User.id).filter(User.id > maxid).order_by(asc(User.id)).all()
        return [x[0] for x in res]

    def get_uninfo_users(self):
        res = self.session.query(User.id).filter(func.coalesce(User.link, '') == '').all()
        return set([x[0] for x in res])

    def get_all_commented_videos(self):
        """
            get all videoIds that have get more than threshold comments in the database.
        """
        threshold = 2000
        res = self.session.query(Comment.video).group_by(Comment.video).having(func.count(Comment.video) > threshold).having(func.count(Comment.video) % 10 != 0).all()
        res = set([x[0] for x in res])
        return res
    
    def get_max_active_user_id(self):
        try:
            maxid = self.session.query(ActiveUser.id).order_by(desc(ActiveUser.id)).limit(1).one()
        except sqlalchemy.orm.exc.NoResultFound as detail:
            maxid = '0'
        return maxid
    # def remove_uncommented_videos(session):
    #     res = session. 
      