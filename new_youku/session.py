# -*- coding: utf-8 -*-
'''
Created on Jun 29, 2015

@author: lin
'''
from vod_orm import *
from exception import *
import sqlalchemy.exc
from sqlalchemy.sql.expression import *
class MySession():
    def __init__(self):
        self.session = self.getSession()
    def close(self):
        self.session.close()

    def getSession(self):
    
        from sqlalchemy import create_engine
        
        engine = create_engine('mysql://root:123456@localhost:3306/new_vod?charset=utf8', encoding='utf-8', echo=False)
        
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
        """
            insert video list, update updatelist, insert userlist.
            videolist only include video with count_number > threshold
        """
    
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

            # the video.user may be None
            if u.id is not None and str(u.id) not in userIdSet:
                userList.append(u)
                userIdSet.add(str(u.id))
            if str(v.id) not in videoIdSet:
#                 
                if v.comment_count > 99:
                    videoList.append(v)
                    videoIdSet.add(str(v.id))
            else:
                updateList.append(v)
    
        for each in userList: 
            print each.id
            self.session.add(each)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            # it is impossible.
            except_stop()
#             print detail
#             self.session.rollback()
        
        # ignore update
#         for each in updateList:
#             try:
#                 originVideo = self.session.query(Video).filter(Video.id == video['id']).one()
#             except sqlalchemy.orm.exc.NoResultFound as detail:
#                 # 说明不需要更新,因为也是在这轮查询中才插入的
#                 continue
#             originVideo.copy(v)
#         try:
#             self.session.commit()
#         except sqlalchemy.exc.IntegrityError as detail:
#             # impossible
#             except_stop()
#             print detail
#             self.session.rollback()
        
        print 'len of videos', len(videoList)
        for each in videoList: self.session.add(each) 
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            # impossible
            except_stop()
#             print detail
#             self.session.rollback()
    
            
            
    def insert_comments(self, comments, users):
        '''
            insert_comment 的多个插入版本
            每次获取的comments的数量是100,对于每个comment,获取其users集合
            对于已经存在的user,过滤掉
            如果存在已经存在的comment,直接放弃这100个comments,转向下一个100comments的获取
            这样做可以让comment每一百提交一次
        '''
        # make User and Comment object to insert.
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
            # it is impossible, because we have filter out existing user.
            except_stop()
#             self.session.rollback()
            
    
        for each in commentList: self.session.add(each)
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as detail:
            # 一定是已经存在comment, 直接放弃
#             except_stop()
            print detail
            print 'abort 100'
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
        """
            it returns the dictionary of <videoId, count_in_comment>.
            use it to judge if a videoId still need searching.
        """

        dict1 = { x[0]:0 for x in self.session.query(Video.id).all()} # all video ids in the database.
        
        # video id existing in comment table, which means it has been searched.
        dict2 = {x[0]:x[1] for 
                 x in self.session.query(Comment.video, func.count(Comment.video)).group_by(Comment.video).all()}
        for d1 in dict1:
            if d1 not in dict2:
                dict2[d1] = dict1[d1]
                
        # the return value is a dictionary.
        # it element is <videoId, count_in_comment>, use it to judge if a video still need to search.
        return dict2
    
    def get_video_by_video(self, video):
        return self.session.query(Video).filter(Video.id == video).one()
    
    def get_videos_by_user(self, user):
        """
            get video commented by user
        """
        videos = self.session.query(Comment.video).filter(Comment.user == user).all()
        res = []
        for video in videos:
            video = video[0]
            v = self.session.query(Video).filter(Video.id == video).one()
            res.append(v)
        return res
    
    def get_all_users(self):
        """
            simply return all userIds in the database.
        """
        res = self.session.query(User.id).all()
        return set([x[0] for x in res])
    
    def get_seq_users(self, maxid):
        res = self.session.query(User.id).filter(User.id > maxid).order_by(asc(User.id)).all()
        return [x[0] for x in res]

    def get_uninfo_users(self):
        res = self.session.query(User.id).filter(func.coalesce(User.link, '') == '').all()
        return set([x[0] for x in res])

    def get_all_commented_videos(self):
        threshlod = 10
        res = self.session.query(Comment.video).group_by(Comment.video).having(func.count(Comment.video) > threshlod).having(func.count(Comment.video) % 10 != 0).all()
        res = set([x[0] for x in res])
        print "size of commented video is: ", len(res)
        return res
    
    def get_all_comments(self):
        res = self.session.query(Comment.video, Comment.user, Comment.published).all()
        videoIdx, userIdx = 0, 0
        videoMap, userMap = {}, {}
        res_list = []
        for comment in res:
            if comment[0] not in videoMap:
                videoMap[comment[0]] = videoIdx
                videoIdx += 1
            if comment[1] not in userMap:
                userMap[comment[1]] = userIdx
                userIdx += 1
            res_list.append((videoMap[comment[0]], userMap[comment[1]]))
            
        return res_list
    
    def get_data(self, train_or_test):
        if train_or_test == "train":
            res = self.session.query(Train.user, Train.video, Train.published).order_by(Train.user, Train.published).all()
        elif train_or_test == "test":
            res = self.session.query(Test.user, Test.video, Test.published).order_by(Test.user, Test.published).all()
        else:
            print "wrong in get_data"
        return res
    def get_test_user_videos(self):
        res = self.session.query(Test.user, Test.video).all()
        return res

if __name__ == '__main__':
    session = MySession()
    session.get_videos_by_user('106764811')

































      