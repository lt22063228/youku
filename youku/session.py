# -*- coding: utf-8 -*-
'''
Created on Jun 29, 2015

@author: lin
'''
from vod_orm import *
import sqlalchemy.exc
def getSession():
    
    from sqlalchemy import create_engine
    
    engine = create_engine('mysql://root:123456@localhost:3306/vod?charset=utf8', encoding='utf-8', echo=False)
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def insert_video(video, session):
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
#     v.toUTF8()
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
def insert_comments(comments, session, users):
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
    for each in userList: session.add(each)
    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError as detail:
        # 一定是已经存在comment, 直接放弃
        print detail
        session.rollback()

    for each in commentList: session.add(each)
    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError as detail:
        # 一定是已经存在comment, 直接放弃
        print detail
        print 'abort 100'
        session.rollback()


        
def insert_comment(comment, session):
    '''
        comment是api返回的视频信息，以dict形式存储，
        若已经存在，则忽略。
        返回信息包含video_id和user_id
    '''
    c = Comment(id = comment['id'], user = comment['user']['id'],
                video = comment['video'], content = comment['content'],
                published = comment['published']
                )
    u = User(id = c.user)
    # 根据视频获取的评论，因此数据库中一定存在相应的视频的信息
    try:
        # 此时用户表中只有一个id字段
        session.add(u)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        # 已经存在这个用户，直接跳过
        session.rollback()
    try:
        session.add(c)
        session.commit()
    except sqlalchemy.exc.IntegrityError as detail:
        # 已经存在这个评论？哪直接跳过吧。
        # 会不会有其他情况，比如不存在相应的视频信息，哪也会出问题
        session.rollback()
        
def insert_favor_by_user(video, userId, session):
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
        session.add(v)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        # 用户收藏的视频已经在数据库中存在，因此就秩序更新视频信息
        session.rollback()
        originVideo = session.query(Video).filter(Video.id == video['id']).one()
        originVideo.copy(v)
        session.commit()
        
    favor = Favor(id = (video.id + '#' + userId), video = video.id, user = userId)
    try:
        session.add(favor)
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        # 收藏关系已经存在数据库中，为什么会这样。。。可能多次运行程序了，
        # 会试图获取同一个用户的收藏视频信息
        # 直接跳过
        session.rollback()
 
def get_all_videos(session):
    res = session.query(Video).all()
    return res

def get_all_users(session):
    res = session.query(User.id).all()
    return set([x[0] for x in res])

def get_all_commented_videos(session):
    res = session.query(Comment.video).group_by(Comment.video).having(func.count(Comment.video) > 100).all()
    res = set([x[0] for x in res])
    return res

# def remove_uncommented_videos(session):
#     res = session. 
  