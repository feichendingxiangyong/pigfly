#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PigFly, Open Source Google Search Solution
# Copyright (C) 2014-2020 WENS FOOD GROUP (<http://www.wens.com.cn>).
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
__author__ = 'Shengli Hu'
__all__ = ['search']

import os
import sys
import time
import tornado.httpclient

from cookielib import LWPCookieJar
from urllib import quote_plus
from urllib2 import Request, urlopen
from urlparse import urlparse, parse_qs
from bs4 import BeautifulSoup


def get_search_result(query):
    # Lazy import of BeautifulSoup.
    # Try to use BeautifulSoup 4 if available, fall back to 3 otherwise.

    #    Prepare the search string.
    query = quote_plus(query)

    f = open("test1.html", 'r')
    html = f.read()

    soup = BeautifulSoup(html)

    # 按照先后顺序分为四组：
    # 1.main_items: 目标组
    # 2.news_leads: 头条组
    # 3.news_sects: 新闻区组
    # 4.norm_items: 一般组
    # 通用分为: top_rel_kws 头部相关搜索，bot_rel_kws 底部相关搜索

    main_items = list()
    news_leads = list()
    news_sects = list()
    norm_items = list()
    top_rel_kws = list()
    bot_rel_kws = list()

    cp_title_main_items = 'div#search div#ires ol#rso li.g div.rc h3.r a'
    cp_dlink_main_items = 'div#search div#ires ol#rso li.g div.rc div.s div div.f.kv._SWb cite._Rm'
    cp_desc_main_items = 'div#search div#ires ol#rso li.g div.rc div.s div span.st'
    cp_title_news_leads = 'div#search div#ires ol#rso li#newsbox.g div._Hnc ol li._njd.scim div.nulead div span._Tyb a._Knc._R7c.l'
    cp_dlink_news_leads = 'div#search div#ires ol#rso li#newsbox.g div._Hnc ol li._njd.scim div.nulead div.gl'
    cp_desc_news_leads = 'div#search div#ires ol#rso li#newsbox.g div._Hnc ol li._njd.scim div.nulead div.s span.st'
    cp_title_news_sects = 'div#search div#ires ol#rso li#newsbox.g div ol li._njd.card-section div.nusec div span._Tyb a._R7c.l'
    cp_dlink_news_sects = 'div#search div#ires ol#rso li#newsbox.g div ol li._njd.card-section div.nusec div.gl'
    cp_title_norm_items = 'div#search div#ires ol#rso div.srg li.g div.rc h3.r a'
    cp_dlink_norm_items = 'div#search div#ires ol#rso div.srg li.g div.rc div.s div div.f.kv._SWb cite._Rm'
    cp_desc_norm_items = 'div#search div#ires ol#rso div.srg li.g div.rc div.s div span.st'
    cp_title_top_rel_kws = 'div#topstuff div#trev.std.card-section div a.nobr'
    cp_title_bot_rel_kws = 'div#botstuff div#brs div.card-section div.brs_col p._e4b a'

    # main items
    tag_title = soup.select(cp_title_main_items)
    tag_dlink = soup.select(cp_dlink_main_items)
    tag_desc = soup.select(cp_desc_main_items)

    z = 0
    for i in tag_title:
        main_items.append({'title': i.get_text(), 'link': i['href'], 'dlink': tag_dlink[z].get_text(),
                           'desc': tag_desc[z].get_text()})
        z += 1

    # news leads
    tag_title = soup.select(cp_title_news_leads)
    tag_dlink = soup.select(cp_dlink_news_leads)
    tag_desc = soup.select(cp_desc_news_leads)

    z = 0
    for i in tag_title:
        news_leads.append({'title': i.get_text(), 'link': i['href'], 'dlink': tag_dlink[z].get_text(),
                           'desc': tag_desc[z].get_text()})
        z += 1

    # news sects  -- no description
    tag_title = soup.select(cp_title_news_sects)
    tag_dlink = soup.select(cp_dlink_news_sects)

    z = 0
    for i in tag_title:
        news_sects.append({'title': i.get_text(), 'link': i['href'], 'dlink': tag_dlink[z].get_text(),
                           'desc': ''})
        z += 1

    # norm items
    tag_title = soup.select(cp_title_norm_items)
    tag_dlink = soup.select(cp_dlink_norm_items)
    tag_desc = soup.select(cp_desc_norm_items)

    z = 0
    for i in tag_title:
        norm_items.append({'title': i.get_text(), 'link': i['href'], 'dlink': tag_dlink[z].get_text(),
                           'desc': tag_desc[z].get_text()})
        z += 1

    # rel keywords
    tag_top = soup.select(cp_title_top_rel_kws)

    z = 0
    for i in tag_top:
        top_rel_kws.append({'title': i.get_text(), 'link': i['href']})
        z += 1

    tag_bot = soup.select(cp_title_bot_rel_kws)

    z = 0
    for i in tag_bot:
        bot_rel_kws.append({'title': i.get_text(), 'link': i['href']})
        z += 1
    return [main_items, news_leads, news_sects, norm_items, top_rel_kws, bot_rel_kws]



def by_replace_page(query, tld='com', lang='en', tbs='0', safe='off', num=10, start=0,
           stop=None, pause=2.0, only_standard=False):
    """
    Search the given query string using Google.

    @type  query: str
    @param query: Query string. Must NOT be url-encoded.

    @type  tld: str
    @param tld: Top level domain.

    @type  lang: str
    @param lang: Languaje.

    @type  tbs: str
    @param tbs: Time limits (i.e "qdr:h" => last hour, "qdr:d" => last 24 hours, "qdr:m" => last month).

    @type  safe: str
    @param safe: Safe search.

    @type  num: int
    @param num: Number of results per page.

    @type  start: int
    @param start: First result to retrieve.

    @type  stop: int
    @param stop: Last result to retrieve.
        Use C{None} to keep searching forever.

    @type  pause: float
    @param pause: Lapse to wait between HTTP requests.
        A lapse too long will make the search slow, but a lapse too short may
        cause Google to block your IP. Your mileage may vary!

    @type  only_standard: bool
    @param only_standard: If C{True}, only returns the standard results from
        each page. If C{False}, it returns every possible link from each page,
        except for those that point back to Google itself. Defaults to C{False}
        for backwards compatibility with older versions of this module.

    @rtype:  generator
    @return: Generator (iterator) that yields found URLs. If the C{stop}
        parameter is C{None} the iterator will loop forever.
    """

    # Lazy import of BeautifulSoup.
    # Try to use BeautifulSoup 4 if available, fall back to 3 otherwise.
    global BeautifulSoup
    if BeautifulSoup is None:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            from BeautifulSoup import BeautifulSoup

    # Set of hashes for the results found.
    # This is used to avoid repeated results.
    hashes = set()

    # Prepare the search string.
    query = quote_plus(query)

    f = open('test1.html', 'r')
    html = f.read()

    f.close()

    # Parse the response and process every anchored URL.
    soup = BeautifulSoup(html)

    # del top
    soup.find(id='gb').decompose()
    print len(soup.find(id='mn').find_all('tbody'))
    print '**********************'
        #tag.decompose()

    # del left
    soup.find(id='leftnav').decompose()

    # del right
    soup.find(id='desktop-search').tr.contents[1].decompose()


    # del bottom
    soup.find(id='bfl').decompose()
    soup.find(id='fll').decompose()

    # del script: 'html body script'
    for tag in soup.find_all('script'):
        tag.decompose()

    style1 = soup.style.extract().prettify(formatter="html")
    style2 = soup.style.extract().prettify(formatter="html")
    table = soup.table.extract().prettify(formatter="html")
    return (style1,style2,table)



if __name__ == '__main__':
    print by_replace_page('abc')
