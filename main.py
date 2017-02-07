import os.path
import cherrypy,time,threading,redis,ast,scrapy,json,requests,argparse
import urllib,time
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
    url = 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/niftyGainers1.json'
    re=requests.get(url)
    js_data=json.loads(re.content)
    stockrate = []
    for i in range(0,10):
        cdict = {}
        cdict['symbol'] = js_data["data"][i]["symbol"]
        cdict['ltp'] = js_data["data"][i]["ltp"]
        cdict['change'] = js_data["data"][i]["netPrice"]
        cdict['traded'] = js_data["data"][i]["tradedQuantity"]
        cdict['value'] = js_data["data"][i]["turnoverInLakhs"]
        cdict['open'] = js_data["data"][i]["openPrice"]
        cdict['high'] = js_data["data"][i]["highPrice"]
        cdict['low'] = js_data["data"][i]["lowPrice"]
        cdict['prevclose'] = js_data["data"][i]["previousPrice"]
        cdict['extntn'] = js_data["data"][i]["lastCorpAnnouncementDate"]
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
