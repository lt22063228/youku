'''
Created on Jul 6, 2015

@author: lin
'''
import logging  
import os

import time
class Client:
    
    def __init__(self):
        self.client_ids = [
    '32e06f6b859adf8e',
    '3d2fc37e70387d54',
    'c4d8012140a55d92',
    '8a1aecc50520fd38',
    '75ca8c221e552d65',
    '3bb3af15c8e29d64',
    'f0271cccdc9ac157',
    '8bb8512725864b73',
    '9c5f810f1c6b0bf0',
    '11203ddf383c2c18',
    'd120b261dd37be58',
    '61db4b7accf13f3d',
    'b1b7acbd056ff90b',
    '3a44f8fec867a9f9',
    '1fcc43cea9d81269',
    '9b189bcb22788678',
    '8de8c8bbf0fb6251',
    '8407ff568b0dc6b4',
    '0990ed7625c24a01',
    '118b47e4fadda985',
    '8de8c8bbf0fb6251',
    ]
        self.counter = 0
        self.length = len(self.client_ids)
        self.t = time.time()
        logging.basicConfig(filename = os.path.join(os.getcwd(), 'client.txt'), level = logging.DEBUG)  
        
    def nextClientId(self):
        temp = self.client_ids[self.counter]
        logging.debug('switch to counter %d' % self.counter)
        logging.debug('duration %s' % (time.time() - self.t))
        self.t = time.time()
        self.counter = (self.counter + 1) % self.length
        return temp
