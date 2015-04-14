#coding=utf-8

import sys
import requests
import re
try: 
    import simplejson as json
except ImportError: 
    import json

'''
sina api:
http://hq.sinajs.cn/list=sh601006

sina format:

0：”大秦铁路”，股票名字； 
1：”27.55″，今日开盘价； 
2：”27.25″，昨日收盘价； 
3：”26.91″，当前价格； 
4：”27.55″，今日最高价； 
5：”26.20″，今日最低价； 
6：”26.91″，竞买价，即“买一”报价； 
7：”26.92″，竞卖价，即“卖一”报价； 
8：”22114263″，成交的股票数，由于股票交易以一百股为基本单位，所以在使用时，通常把该值除以一百； 
9：”589824680″，成交金额，单位为“元”，为了一目了然，通常以“万元”为成交金额的单位，所以通常把该值除以一万； 
10：”4695″，“买一”申请4695股，即47手； 
11：”26.91″，“买一”报价； 
12：”57590″，“买二” 
13：”26.90″，“买二” 
14：”14700″，“买三” 
15：”26.89″，“买三” 
16：”14300″，“买四” 
17：”26.88″，“买四” 
18：”15100″，“买五” 
19：”26.87″，“买五” 
20：”3100″，“卖一”申报3100股，即31手； 
21：”26.92″，“卖一”报价 
(22, 23), (24, 25), (26,27), (28, 29)分别为“卖二”至“卖四的情况” 
30：”2008-01-11″，日期； 
31：”15:05:32″，时间；



163 api:
http://api.money.126.net/data/feed/1000049

163 format:
_ntes_quote_callback({"1000049":{"code": "1000049", "percent": 0.021511, "high": 37.3, "askvol3": 16015, "askvol2": 3500, "askvol5": 5700, "askvol4": 10210, "price": 37.04, "open": 36.33, "bid5": 36.95, "bid4": 36.96, "bid3": 36.98, "bid2": 36.99, "bid1": 37.0, "low": 36.15, "updown": 0.78, "type": "SZ", "bidvol1": 5800, "status": 0, "bidvol3": 52300, "bidvol2": 13000, "symbol": "000049", "update": "2015/02/16 11:13:16", "bidvol5": 7800, "bidvol4": 2800, "volume": 2646582, "askvol1": 1800, "ask5": 37.07, "ask4": 37.06, "ask1": 37.03, "name": "\u5fb7\u8d5b\u7535\u6c60", "ask3": 37.05, "ask2": 37.04, "arrow": "\u2191", "time": "2015/02/16 11:13:09", "yestclose": 36.26, "turnover": 97506086.72} });
'''

class StockInfo(object):
    
    def __init__(self):
        self.code = 0
        self.name = 0
        self.target_price = 0
        self.price = 0
        self.low = 0
        self.high = 0
        self.percent = 0
    def __str__(self):
        return "name:%s, price:%d, target_price: %d" % (self.name, self.price, self.target_price)

class StockFetcher():
    def __init__(self, data_file):
        self.data_file = data_file
        self.base_url_sina = "http://hq.sinajs.cn/list="
        self.base_url_163 = "http://api.money.126.net/data/feed/"
        self.reg_163 = re.compile(r"_ntes_quote_callback\((.*)\)")

    def load_data(self):
        stock_infos = []
        for line in open(self.data_file).readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            tokens = line.split(" ")
            if len(tokens) != 3:
                continue
            stock_info = StockInfo()
            stock_info.code = tokens[0]
            stock_info.name = tokens[1]
            stock_info.target_price = float(tokens[2])
            stock_infos.append(stock_info)
        self.stock_infos = stock_infos

    def execute(self):
        self.load_data()
        for stock_info in self.stock_infos:
            status = self.fetch_from_163(stock_info)
            if not status:
                print "163 stock api format error"
                return
    
        for stock_info in self.stock_infos:
            if stock_info.price < stock_info.target_price:
                print stock_info

    def fetch_from_sina(self, stock_code):

        #url = self.base_url + "sh601006"
        url = self.base_url_sina + stock_code
        stock_data_raw = requests.get(url).text
        if stock_data_raw is not None:
            tokens = stock_data_raw.split("\"")
            if len(tokens) == 3:
                params = tokens[1].split(",")
                current_price = params[3]
                print current_price
    
    def fetch_from_163(self, stock_info):
        url = self.base_url_163 + stock_info.code
        stock_data_raw = requests.get(url).text
        if stock_data_raw is not None:
            m = self.reg_163.search(stock_data_raw)
            if m:
                stock_data = m.group(1)
                stock_data_json = json.loads(stock_data, "utf-8")
                stock_data_dict = stock_data_json[stock_info.code]
                stock_info.price = float(stock_data_dict['price'])
                stock_info.low = float(stock_data_dict['low'])
                stock_info.high = float(stock_data_dict['high'])
                stock_info_percent = float(stock_data_dict['percent'])
                return True
        return False 

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s <stock_data_file>" % (sys.argv[0])
        sys.exit()
    fetcher = StockFetcher(sys.argv[1])
    fetcher.execute()
