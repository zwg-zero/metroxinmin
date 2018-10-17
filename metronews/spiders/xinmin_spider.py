# -*- coding: utf-8 -*-

"""
    scrapy spider for get news from xinmin
"""

import scrapy
import logging
from ..items import MetroNewsItem
import re


# start urls to get news from
XINMIN_URLS = [
    'http://shanghai.xinmin.cn/tfbd/',  # 头条 => 突发
    'http://shanghai.xinmin.cn/xmsq/',  # 头条 => 新民社会
    'http://newsxmwb.xinmin.cn/xinminyx/pc/',  # 头条 => 新民印象
    'http://newsxmwb.xinmin.cn/chengsh/pc/',  # 民生  => 城市生活
]
PAGES_FIND_PATENT = '//div[@class="fenye"]/div[@class="pageBox"]/a/@href'  # xpath to find the fenye div
SUMMARY_FIND_PATENT = '//div[@class="type_content_list"]/div'
DETAIL_FIND_PATENT = '//div[@class="PageCore"]/div[@class="Cleft"]'


class XinMinSpider(scrapy.Spider):
    name = 'xinmin'  # this spider name, should unique in this project

    def start_request(self):
        urls = XINMIN_URLS
        for url in urls:
            yield scrapy.Request(url=url, callback=self.page_parse)

    def page_parse(self, response):
        # this parse will extract pages url in each XINMIN_URLS
        # normally there will be 10 pages for each url
        # xpath like: div class="PageCoreBg body list-page app_list_pc"/div class="PageCore grids100/"
        # div class="w-79 main" /div class="fenye clearfix" / div class="pageBox" / <a href="index.html"
        # <a href="index_2.html"
        pages_short_urls = response.selector.xpath(PAGES_FIND_PATENT).extract()
        if not pages_short_urls:
            logging.error("No pages find")
            return None

        # get ride of duplicated page url and return full url of page
        pages_full_urls = self.make_unique_urls(response, pages_short_urls)
        for full_url in pages_full_urls:
            yield scrapy.Request(full_url, callable=self.summary_parse)

    @staticmethod
    def make_unique_urls(response, url_list):
        url_set = set(*url_list)
        url_unique_list = []
        for short_url in url_set:
            base_url = response.request.url
            url_unique_list.append(base_url + short_url)
        return url_unique_list

    def summary_parse(self, response):
        # extract news summary
        news_list_div = response.selector.xpath(SUMMARY_FIND_PATENT)
        for news_div in news_list_div:
            news_item = MetroNewsItem()
            news_item['summary_pic_url'] = news_div.xpath('a/img/@src').extract()
            news_item['title'] = news_div.xpath('div/a/text()').extract()
            url = news_div.xpath('div/a/@href').extract()
            news_item['summary_content'] = news_div.xpath('div/p/text()').extract()
            news_item['datetime'] = news_div.xpath('div/div/span/text()').extract()
            yield scrapy.Request(url, callback=self.detail_parse, meta=news_item)

    def detail_parse(self, response):
        item = response.meta
        # extract news detail
        news_page_core = response.selector.xpath(DETAIL_FIND_PATENT)

        # get source_tags string
        item['source_tags'] = news_page_core.xpath('div[@class="Mbx"]/text()').extract().replace("您现在的位置：首页 >", '')

        article_box = news_page_core.xpath('div[@class="ArticleBox"]')
        # get source, journalist and editor
        info_list = article_box.xpath('div[@class="info"]/span').extract()
        for each_info in info_list:
            source_match = re.match(r'来源：(.*)', each_info)
            if source_match:
                item['source'] = source_match.group(1)
            journalist_match = re.match(r'记者：', each_info)
            if journalist_match:
                item['journalist'] = source_match.group(1)
            editor_match = re.match(r'编辑：', each_info)
            if editor_match:
                item['editor'] = source_match.group(1)

        # get content and image urls
        content_box_p = article_box.xpath('div[@class="a_content"]/p')
        item['detailed_content'] =




















