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
data = """1    123.125.116.241    20308    HTTP    北京市 联通ADSL    02-14 01:40    0.994    whois
2    219.234.82.88    5618    HTTP    北京市 电信通IDC机房    02-14 01:40    0.997    whois
3    219.234.82.90    21270    HTTP    北京市 电信通IDC机房    02-14 01:40    4.000    whois
4    123.125.116.243    12737    HTTP    北京市 联通ADSL    02-14 01:40    0.998    whois
5    123.125.116.241    17403    HTTP    北京市 联通ADSL    02-14 01:40    1.007    whois
6    219.234.82.78    20877    HTTP    北京市 电信通IDC机房    02-14 01:40    5.003    whois
7    123.125.116.243    34109    HTTP    北京市 联通ADSL    02-14 01:39    1.002    whois
8    219.234.82.83    9090    HTTP    北京市 电信通IDC机房    02-14 01:39    1.000    whois
9    123.125.116.241    9000    HTTP    北京市 联通ADSL    02-14 01:39    1.002    whois
10    123.125.116.241    16649    HTTP    北京市 联通ADSL    02-14 01:39    0.991    whois
11    219.234.82.86    23685    HTTP    北京市 电信通IDC机房    02-14 01:39    3.007    whois
12    219.234.82.86    3161    HTTP    北京市 电信通IDC机房    02-14 01:39    1.001    whois
13    123.125.116.241    32793    HTTP    北京市 联通ADSL    02-14 01:39    1.005    whois
14    123.125.116.243    8160    HTTP    北京市 联通ADSL    02-14 01:39    0.995    whois
15    123.125.116.243    8541    HTTP    北京市 联通ADSL    02-14 01:39    0.993    whois
16    123.125.116.242    9029    HTTP    北京市 联通ADSL    02-14 01:38    1.002    whois
17    123.125.116.242    14105    HTTP    北京市 联通ADSL    02-14 01:38    0.999    whois
18    219.234.82.87    20621    HTTP    北京市 电信通IDC机房    02-14 01:38    1.006    whois
19    123.125.116.243    22085    HTTP    北京市 联通ADSL    02-14 01:38    1.002    whois
20    123.125.116.243    27545    HTTP    北京市 联通ADSL    02-14 01:38    1.000    whois
21    219.234.82.78    31565    HTTP    北京市 电信通IDC机房    02-14 01:38    1.004    whois
22    123.125.116.242    17183    HTTP    北京市 联通ADSL    02-14 01:38    1.009    whois
23    120.197.85.182    20125    HTTP    广东省广州市 移动    02-14 01:38    0.991    whois
24    219.234.82.90    33730    HTTP    北京市 电信通IDC机房    02-14 01:38    2.011    whois
25    123.125.116.243    26522    HTTP    北京市 联通ADSL    02-14 01:38    1.002    whois
26    123.125.116.241    8817    HTTP    北京市 联通ADSL    02-14 01:38    1.006    whois
27    219.234.82.83    6133    HTTP    北京市 电信通IDC机房    02-14 01:38    6.000    whois
28    123.125.116.241    7806    HTTP    北京市 联通ADSL    02-14 01:37    1.005    whois
29    123.125.116.242    23685    HTTP    北京市 联通ADSL    02-14 01:37    0.996    whois
30    219.234.82.83    9660    HTTP    北京市 电信通IDC机房    02-14 01:37    3.994    whois
31    123.125.116.243    33919    HTTP    北京市 联通ADSL    02-14 01:37    1.005    whois
32    123.125.116.241    33911    HTTP    北京市 联通ADSL    02-14 01:37    1.001    whois
33    219.234.82.90    20995    HTTP    北京市 电信通IDC机房    02-14 01:37    1.004    whois
34    123.125.116.243    6802    HTTP    北京市 联通ADSL    02-14 01:37    1.002    whois
35    123.125.116.243    33976    HTTP    北京市 联通ADSL    02-14 01:37    0.999    whois
36    219.234.82.86    39983    HTTP    北京市 电信通IDC机房    02-14 01:37    3.997    whois
37    123.125.116.241    5651    HTTP    北京市 联通ADSL    02-14 01:37    0.996    whois
38    123.125.116.243    8639    HTTP    北京市 联通ADSL    02-14 01:37    1.001    whois
39    123.125.116.241    9029    HTTP    北京市 联通ADSL    02-14 01:37    1.003    whois
40    120.197.85.182    20367    HTTP    广东省广州市 移动    02-14 01:37    1.000    whois
41    123.125.116.241    20173    HTTP    北京市 联通ADSL    02-14 01:37    1.005    whois
42    123.125.116.243    33942    HTTP    北京市 联通ADSL    02-14 01:36    1.009    whois
43    219.234.82.86    34032    HTTP    北京市 电信通IDC机房    02-14 01:36    0.998    whois
44    219.234.82.77    9090    HTTP    北京市 电信通IDC机房    02-14 01:36    0.998    whois
45    123.125.116.241    36081    HTTP    北京市 联通ADSL    02-14 01:36    1.003    whois
46    219.234.82.60    8000    HTTP    北京市 电信通IDC机房    02-14 01:36    6.010    whois
47    123.125.116.243    9090    HTTP    北京市 联通ADSL    02-14 01:36    1.002    whois
48    123.125.116.241    8160    HTTP    北京市 联通ADSL    02-14 01:36    1.001    whois
49    123.125.116.243    8788    HTTP    北京市 联通ADSL    02-14 01:36    1.000    whois
50    123.125.116.241    5616    HTTP    北京市 联通ADSL    02-14 01:36    1.003    whois
51    123.125.116.243    24775    HTTP    北京市 联通ADSL    02-14 01:36    1.004    whois
52    123.125.116.241    8755    HTTP    北京市 联通ADSL    02-14 01:36    1.003    whois
53    219.234.82.53    28670    HTTP    北京市 电信通IDC机房    02-14 01:36    0.999    whois
54    219.234.82.62    31844    HTTP    北京市 电信通IDC机房    02-14 01:36    2.002    whois
55    123.125.116.243    5881    HTTP    北京市 联通ADSL    02-14 01:36    0.995    whois
56    123.125.116.243    39513    HTTP    北京市 联通ADSL    02-14 01:36    0.993    whois
57    219.234.82.76    8489    HTTP    北京市 电信通IDC机房    02-14 01:36    5.004    whois
58    219.234.82.75    20491    HTTP    北京市 电信通IDC机房    02-14 01:35    1.007    whois
59    123.125.116.243    26556    HTTP    北京市 联通ADSL    02-14 01:35    1.002    whois
60    123.125.116.243    39831    HTTP    北京市 联通ADSL    02-14 01:35    1.003    whois
61    123.125.116.243    34034    HTTP    北京市 联通ADSL    02-14 01:35    1.006    whois
62    123.125.116.243    8939    HTTP    北京市 联通ADSL    02-14 01:35    4.001    whois
63    123.125.116.243    29294    HTTP    北京市 联通ADSL    02-14 01:35    1.000    whois
64    219.234.82.76    8087    HTTP    北京市 电信通IDC机房    02-14 01:35    1.007    whois
65    123.125.116.241    12121    HTTP    北京市 联通ADSL    02-14 01:35    0.993    whois
66    123.125.116.241    11095    HTTP    北京市 联通ADSL    02-14 01:35    0.989    whois
67    120.197.85.182    20371    HTTP    广东省广州市 移动    02-14 01:35    1.007    whois
68    219.234.82.75    11070    HTTP    北京市 电信通IDC机房    02-14 01:35    1.001    whois
69    123.125.116.241    13789    HTTP    北京市 联通ADSL    02-14 01:35    1.004    whois
70    219.234.82.83    5978    HTTP    北京市 电信通IDC机房    02-14 01:35    2.010    whois
71    219.234.82.78    33635    HTTP    北京市 电信通IDC机房    02-14 01:34    1.007    whois
72    123.125.116.243    23862    HTTP    北京市 联通ADSL    02-14 01:34    1.012    whois
73    123.125.116.243    24379    HTTP    北京市 联通ADSL    02-14 01:34    1.012    whois
74    123.125.116.241    6022    HTTP    北京市 联通ADSL    02-14 01:34    0.998    whois
75    219.234.82.90    38217    HTTP    北京市 电信通IDC机房    02-14 01:34    0.997    whois
76    123.125.116.241    6370    HTTP    北京市 联通ADSL    02-14 01:34    1.009    whois
77    123.125.116.243    9571    HTTP    北京市 联通ADSL    02-14 01:34    0.995    whois
78    123.125.116.243    14826    HTTP    北京市 联通ADSL    02-14 01:34    0.998    whois
79    123.125.116.243    34778    HTTP    北京市 联通ADSL    02-14 01:34    1.002    whois
80    123.125.116.242    31755    HTTP    北京市 联通ADSL    02-14 01:34    1.002    whois
81    123.125.116.241    6938    HTTP    北京市 联通ADSL    02-14 01:34    0.997    whois
82    219.234.82.87    8080    HTTP    北京市 电信通IDC机房    02-14 01:34    0.996    whois
83    123.125.116.241    6484    HTTP    北京市 联通ADSL    02-14 01:34    1.008    whois
84    123.125.116.242    20770    HTTP    北京市 联通ADSL    02-14 01:33    0.998    whois
85    123.125.116.243    20847    HTTP    北京市 联通ADSL    02-14 01:33    1.006    whois
86    219.234.82.90    10290    HTTP    北京市 电信通IDC机房    02-14 01:33    1.006    whois
87    42.120.51.102    20586    HTTP    上海市 阿里巴巴软件(上海)有限公司    02-14 01:33    1.012    whois
88    219.234.82.54    29037    HTTP    北京市 电信通IDC机房    02-14 01:33    1.006    whois
89    219.234.82.74    9090    HTTP    北京市 电信通IDC机房    02-14 01:33    1.008    whois
90    219.234.82.79    17495    HTTP    北京市 电信通IDC机房    02-14 01:33    3.990    whois
91    123.125.116.243    9999    HTTP    北京市 联通ADSL    02-14 01:33    1.004    whois
92    219.234.82.90    11790    HTTP    北京市 电信通IDC机房    02-14 01:33    2.000    whois
93    123.125.116.242    5547    HTTP    北京市 联通ADSL    02-14 01:33    1.007    whois
94    123.125.116.243    36081    HTTP    北京市 联通ADSL    02-14 01:33    0.995    whois
95    123.125.116.243    21238    HTTP    北京市 联通ADSL    02-14 01:33    0.999    whois
96    123.125.116.243    17945    HTTP    北京市 联通ADSL    02-14 01:33    1.000    whois
97    123.125.116.242    17403    HTTP    北京市 联通ADSL    02-14 01:32    1.000    whois
98    123.125.116.243    13669    HTTP    北京市 联通ADSL    02-14 01:32    1.000    whois
99    123.125.116.243    20771    HTTP    北京市 联通ADSL    02-14 01:32    1.007    whois
100    219.234.82.88    24438    HTTP    北京市 电信通IDC机房    02-14 01:32    5.999    whois
"""    
    
    
class Proxy:

    def __init__(self):
        self.filters = {}
        self.getProxy()
        self.t = time.time()
        logging.basicConfig(filename = os.path.join(os.getcwd(), 'proxy.txt'), level = logging.DEBUG)  
    
    def getIndex(self):
        return self.result[0][0]
    
    def nextProxy(self):
        return
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
        return
        url = 'http://www.proxy.com.ru/list_'
        self.result = []
        self.counter = 0
        for i in range(1, 8):
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
    p = Proxy()
    p.getProxy()
    proxy = "http://111.13.12.216:80"
#     url = "https://openapi.youku.com/v2/users/show.json"
    url = "http://www.baidu.com"
    r = requests.get(url,proxies = {'https':proxy, 'http':proxy})
#     r = requests.get(url)
    print r.text
    pass

