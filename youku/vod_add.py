'''
Created on Jun 29, 2015

@author: lin
'''
from vod_orm import *
import session
import sqlalchemy.exc

session = session.getSession()
newUser = User(name='tom', id=23)
newVideo = Video(title = 'testvideo', id = 24)
user = session.query(User).filter(User.id == '23').one()
print '..'
print user
print '..'
newVideo.user = newUser.id
try:
    
    session.add(newUser)
    session.add(newVideo)
    res = session.query(Video).all()
    print res[0].title
    print newVideo
    session.commit()
except sqlalchemy.exc.IntegrityError as detail:
    print type(detail)

