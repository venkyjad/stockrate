import os.path
import cherrypy,time,threading,redis,ast,scrapy,json,requests,argparse
from bs4 import BeautifulSoup
from lxml import etree
import urllib,time
from selenium import webdriver
from mako.template import Template
from cherrypy.process.plugins import Monitor

class MainProgram:
    @cherrypy.expose
    def index(self):
        r = redis.Redis("localhost")
        get_stock_rate()
        sr = r.lrange('stl',0,10)
        stock = []
        for i in range(10):
            d = ast.literal_eval(sr[i])
            stock.append(d)
        stock =  stock[::-1]
        return Template(filename='index.html').render(data=stock)


def get_stock_rate():
    #This Thread Gets the Data Every 5minutes and Updates to Redis
    threading.Timer(300, get_stock_rate).start()
    r = redis.Redis("localhost")
    browser = webdriver.PhantomJS()
    browser.get('https://www.nseindia.com/live_market/dynaContent/live_analysis/top_gainers_losers.htm?cat=G')
    soup = BeautifulSoup(browser.page_source, "html.parser")
    table = soup.find('table', {'id': 'topGainers'})
    stockrate = []
    for row in table.find_all('tr')[1:]:
        cdict = {}
        col = row.find_all('td')
        cdict['symbol'] = col[0].string.strip()
        cdict['ltp'] = col[1].string.strip()
        cdict['change'] = col[2].string.strip()
        cdict['traded'] = col[3].string.strip()
        cdict['value'] = col[4].string.strip()
        cdict['open'] = col[5].string.strip()
        cdict['high'] = col[6].string.strip()
        cdict['low'] = col[7].string.strip()
        cdict['prevclose'] = col[8].string.strip()
        cdict['extntn'] = col[9].string.strip()
        stockrate.append(cdict)
        r.lpush('stl',cdict)
    sr = r.lrange('stl',0,10)
    print "Getting Data Every 5 minutes"
    return stockrate

get_stock_rate()
config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 5000)),
    }
}
cherrypy.quickstart(MainProgram(), '/', config=config)
