# -*- coding: utf-8 -*-
'''
Created on Jul 6, 2015

@author: lin
'''

import requests
import time
from bs4 import BeautifulSoup
import logging  
import os
class Proxy:

    def __init__(self):
        self.filters = {}
        self.getProxy()
        self.t = time.time()
        logging.basicConfig(filename = os.path.join(os.getcwd(), 'proxy.txt'), level = logging.DEBUG)  
    
    def getIndex(self):
        return self.result[0][0]
    
    def nextProxy(self):
        del self.result[self.counter]
        self.length = len(self.result)
        if self.length < 5:
            self.getProxy()
            print 'getting proxy again'
        index, ip, port, location = self.result[self.counter]
        
        logging.debug("switch to index %s, location %s" % (index, location))
        logging.debug('duration %s' % (time.time() - self.t))
        self.t = time.time()
        res = 'http://' + ip + ':' + port
        print 'change proxy to', res
        return res
    
    def getProxy(self):
    
        url = 'http://www.proxy.com.ru/list_'
        self.result = []
        self.counter = 0
        for i in range(1, 3):
            print 'proxy...', i
            realUrl = url + str(i) + '.html'
            html = requests.get(realUrl)
            html = html.text
            
            soup = BeautifulSoup(html, 'html.parser')
            count = 0
    
            for each in soup.center.contents[5].tr.contents[3].table.contents[2:]:
                if count % 2 == 0: 
                    count += 1
                    continue
                index = str(each.find_all('td')[0].string)
                ip = str(each.find_all('td')[1].string)
                port = str(each.find_all('td')[2].string)
                location = unicode(each.find_all('td')[4].string).encode('utf8')

                self.result.append((index, ip, port, location))
                count += 1
          
        self.length = len(self.result)
        
if __name__ == '__main__':
#     p = Proxy()
#     p.getProxy()
    pass

    
        
    
    