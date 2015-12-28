# -*- coding: utf-8 -*-
'''
Created on Jun 29, 2015

@author: lin
'''



from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

Base = declarative_base()

class Video(Base):
    __tablename__ = 'video'
    id = Column(String(60), primary_key = True)
    title = Column(String(60))
    link = Column(String(60))
    duration = Column(Integer)
    category = Column(String(60))
    view_count = Column(Integer)
    favorite_count = Column(Integer)
    comment_count = Column(Integer)
    up_count = Column(Integer)
    down_count = Column(Integer)
    published = Column(DateTime)
    genre = Column(String(60))
    # 上传视频的用户id
    user = Column(String(60), ForeignKey('user.id'))
    favorite_time = Column(DateTime)
    
    def copy(self, video):
        self.id = video.id
        self.title = video.title
        self.link = video.link
        self.duration = video.duration
        self.category = video.category
        self.view_count = video.view_count
        self.favorite_count = video.favorite_count
        self.comment_count = video.comment_count
        self.up_count = video.up_count
        self.down_count = video.down_count
        self.published = video.published
        self.user = video.user
        
    
    def __repr__(self):
        return "<video %s %s>" % (self.id, self.title)

class User(Base):
    __tablename__ = 'user'
    id = Column(String(60), primary_key = True)
    name = Column(String(60))
    link = Column(String(60))
    gender = Column(String(60))
    description = Column(String(200))
    videos_count = Column(Integer)
    playlist_count = Column(Integer)
    favorites_count = Column(Integer)
    followers_count = Column(Integer)
    following_count = Column(Integer)
    statuses_count = Column(Integer)
    vv_count = Column(Integer)
    regist_time = Column(DateTime)
    
    def copy(self, user):
        self.id              = user.id
        self.name            = user.name
        self.link            = user.link
        self.gender          = user.gender
        self.description     = user.description
        self.videos_count    = user.videos_count
        self.playlist_count  = user.playlist_count
        self.favorites_count = user.favorites_count
        self.followers_count = user.followers_count
        self.following_count = user.following_count
        self.statuses_count  = user.statuses_count
        self.vv_count        = user.vv_count
        self.regist_time     = user.regist_time

    def __repr__(self):
        return "<user %s %s>" % (self.id, self.name)
class ActiveUser(Base):
    __tablename__ = 'active_user'
    id = Column(String(60), primary_key = True)
    name = Column(String(60))
    link = Column(String(60))
    gender = Column(String(60))
    description = Column(String(200))
    videos_count = Column(Integer)
    playlist_count = Column(Integer)
    favorites_count = Column(Integer)
    followers_count = Column(Integer)
    following_count = Column(Integer)
    statuses_count = Column(Integer)
    vv_count = Column(Integer)
    regist_time = Column(DateTime)
    
    def copy(self, user):
        self.id              = user.id
        self.name            = user.name
        self.link            = user.link
        self.gender          = user.gender
        self.description     = user.description
        self.videos_count    = user.videos_count
        self.playlist_count  = user.playlist_count
        self.favorites_count = user.favorites_count
        self.followers_count = user.followers_count
        self.following_count = user.following_count
        self.statuses_count  = user.statuses_count
        self.vv_count        = user.vv_count
        self.regist_time     = user.regist_time

    
 

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(String(60), primary_key=True)
    content = Column(String(200))
    published = Column(DateTime)
    # 发表评论的用户id
    user = Column(String(60), ForeignKey('user.id'))
    # 被评论的视频的id
    video = Column(String(60), ForeignKey('video.id'))

    def __repr__(self):
        return "<comment %s %s>" % (self.id, self.content)
    
class Favor(Base):
    __tablename__ = 'favor'
    # id 是userid和videoid通过#符号拼接而成
    id = Column(String(120), primary_key = True)
    user = Column(String(60), ForeignKey('user.id'))
    video = Column(String(60), ForeignKey('video.id'))
    
    def __repr__(self):
        return "<favor %s %s>" % (self.id, self.content)
    
if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine('mysql://root:123456@localhost:3306/vod?charset=utf8', echo=False)
    Base.metadata.create_all(engine)