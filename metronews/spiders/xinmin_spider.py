# -*- coding: utf-8 -*-

"""
    scrapy spider for get news from xinmin
"""

import scrapy

# start urls to get news from
XINMIN_URL = [
    'http://shanghai.xinmin.cn/tfbd/',  # 头条 => 突发
    'http://shanghai.xinmin.cn/xmsq/',  # 头条 => 新民社会
    'http://newsxmwb.xinmin.cn/xinminyx/pc/index.htm',  # 头条 => 新民印象
    'http://newsxmwb.xinmin.cn/chengsh/pc/index.htm',  # 民生  => 城市生活
]


class XinMinSpider(scrapy.Spide):
    name = 'xinmin'  # this spider name, should unique in this project

    def start_request(self):
        urls = XINMIN_URL
        for url in urls:
            yield scrapy.Request(url=url, callback=self.page_parse)

    # this parse will extract pages url in this first page
    # normally there will be 10 pages for each url
    # xpath like: div class="PageCoreBg body list-page app_list_pc"/div class="PageCore grids100/"
    # div class="w-79 main" /div class="fenye clearfix" / div class="pageBox" / <a href="index.html"
    # <a href="index_2.html"
    def page_parse(self, response):


