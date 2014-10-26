#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# PigFly, Open Source Google Search Solution
#    Copyright (C) 2014-2020 WENS FOOD GROUP (<http://www.wens.com.cn>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    Authored by Shengli Hu <hushengli@gmail.com>
##############################################################################
__author__ = 'Shengli Hu'
import os
import re
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.httpclient
from gosearch import by_replace_page
from gosearch import filter_result
from tornado.options import define, options  

define("port", default=8000, help="Run server on a specific port", type=int)  

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template/index.html")


class GotoHandler(tornado.web.RequestHandler):
    def get(self):
        url = '/url?q='+self.get_argument('q')
	url = filter_result(url)
        if not url:
            url = '/'
        logging.info(self.request.remote_ip+'\tgoto:\t' + url)
        self.redirect(url)


class SearchHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        # google the result
        keywords = self.get_argument("q")
        #if keywords:
        #    p = re.compile('[\s]+')
        #    # keywords = p.sub('+', keywords)
        #    keywords, number = p.subn('+', keywords)

        logging.info(self.request.remote_ip +'\tsearch for:\t'+keywords)
        query = keywords.encode('utf-8')
        # entries = list()
        # (style1, style2, table) = by_replace_page(keywords,stop=30)

        self.render("template/result.html", result=by_replace_page(query,tld='com',lang='zh',num=40,stop=30,pause=0))

    def on_response(self, response):
        if response.error:
            raise tornado.web.HTTPError(500)
        entries = response.body
        #json = tornado.escape.json_decode(response.body)
        pass

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "342ezKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "xsrf_cookies": True,
    "debug": False,
}
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/url", GotoHandler),
    (r"/search", SearchHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
], **settings)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    tornado.options.parse_command_line()
    http_server.listen(options.port)  
    tornado.ioloop.IOLoop.instance().start()
