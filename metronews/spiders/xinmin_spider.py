# -*- coding: utf-8 -*-

"""
    scrapy spider for get news from xinmin
"""

import scrapy
import logging
import re
from datetime import datetime as dt
from datetime import timedelta

from ..items import MetroNewsItem

# start urls to get news from
XINMIN_URLS = [
    'http://shanghai.xinmin.cn/tfbd/',  # 头条 => 突发
    'http://shanghai.xinmin.cn/xmsq/',  # 头条 => 新民社会
    'http://newsxmwb.xinmin.cn/xinminyx/pc/',  # 头条 => 新民印象
    'http://newsxmwb.xinmin.cn/chengsh/pc/',  # 民生  => 城市生活
]

# xpath find elements string
# in summary page
PAGES_FIND_PATENT = '//div[normalize-space(@class)="fenye clearfix"]/div[normalize-space(@class)="pageBox"]/a/@href'  # xpath to find the fenye div
SUMMARY_FIND_PATENT = '//div[normalize-space(@class)="type_content_list type-item"]/div'
SUMMARY_PIC_URL_FIND_PATENT = 'a/img/@src'
URL_FIND_PATENT = 'a/@href'
TITLE_FIND_PATENT = 'div/a/text()'
SUMMARY_CONTENT_FIND_PATENT = 'div/p/text()'
DATETIME_FIND_PATENT = 'div/div[@class="info"]/span'

# in detailed page
DETAIL_FIND_PATENT = '//div[normalize-space(@class)="PageCore"]/div[normalize-space(@class)="Cleft"]'
ARTICLE_FIND_PATENT = 'div[normalize-space(@class)="ArticleBox"]'
INFO_FIND_PATENT = 'div[normalize-space(@class)="info"]/span/text()'
SOURCE_TAGS_FIND_PATENT = 'div[normalize-space(@class)="Mbx"]/text()'
CONTENT_BOX_FIND_PATENT = 'div[normalize-space(@class)="a_content"]/p'
CONTENT_LEN_MIN = 30  # when filter detailed news p element, if length of message less than this value, will be delete
# source, editor, journalist find re patent
RE_SOURCE_PATENT = re.compile(r'来源：(.*)')
RE_JOURNALIST_PATENT = re.compile(r'记者：(.*)')
RE_EDITOR_PATENT = re.compile(r'编辑：(.*)')
RE_DATETIME_FIND_PATENT = re.compile(r'.*(\d\d\d\d-\d\d-\d\d \d\d:\d\d).*')

# filter news which content contain special words
RE_WORDS_FILTER = re.compile(r'[mM]etro|[Ss]ubway|地铁')
# only get the latest 2 days, this is only for test.
LATEST_DAYS = 2


class XinMinSpider(scrapy.Spider):
    name = 'xinmin'  # this spider name, should unique in this project

    def start_requests(self):
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
            yield scrapy.Request(full_url, callback=self.summary_parse)

    @staticmethod
    def make_unique_urls(response, url_list):
        url_set = set(url_list)
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
            news_item['summary_pic_url'] = news_div.xpath(SUMMARY_PIC_URL_FIND_PATENT).extract_first()
            news_item['title'] = news_div.xpath(TITLE_FIND_PATENT).extract_first()
            url = news_div.xpath(URL_FIND_PATENT).extract_first()
            news_item['summary_content'] = news_div.xpath(SUMMARY_CONTENT_FIND_PATENT).extract_first().strip()

            # get datetime
            datetime_spans = news_div.xpath(DATETIME_FIND_PATENT)
            if datetime_spans:
                datetime = datetime_spans[-1].xpath('text()').extract_first()
                if not datetime:
                    raise ValueError('parse datetime error, not get datetime')
                # assert datetime get is really a datetime
                if not re.match(RE_DATETIME_FIND_PATENT, datetime):
                    raise ValueError("datetime error, parse error, get: %s" % datetime)
                # compare datetime with latest news date we already have to filter only newer news we would process
                # you should change the below according to your situation
                if dt.strptime(datetime, "%Y-%m-%d %H:%M") < dt.now() - timedelta(days=LATEST_DAYS):
                    continue
                news_item['datetime'] = datetime.strip()

            else:
                raise ValueError('Not find the datetime.')
            yield scrapy.Request(url, callback=self.detail_parse, meta=news_item)

    def detail_parse(self, response):
        item = response.meta
        # extract news detail
        news_page_core = response.selector.xpath(DETAIL_FIND_PATENT)

        # get source_tags string
        source_tag_text = news_page_core.xpath(SOURCE_TAGS_FIND_PATENT).extract_first()
        if source_tag_text:
            item['source_tags'] = source_tag_text.replace("您现在的位置：首页 >", '').strip().replace(">", '')

        article_box = news_page_core.xpath(ARTICLE_FIND_PATENT)
        # get source, journalist, editor and datetime
        info_list = article_box.xpath(INFO_FIND_PATENT).extract()
        for each_info in info_list:
            source_match = re.match(RE_SOURCE_PATENT, each_info)
            if source_match:
                item['source'] = source_match.group(1)
                continue
            journalist_match = re.match(RE_JOURNALIST_PATENT, each_info)
            if journalist_match:
                item['journalist'] = journalist_match.group(1)
                continue
            editor_match = re.match(RE_EDITOR_PATENT, each_info)
            if editor_match:
                item['editor'] = editor_match.group(1)
            #    continue
            # date_time_match = re.match(RE_DATETIME_FIND_PATENT, each_info)
            # if date_time_match:
            #     item['datetime'] = date_time_match.group(1)

        # get content and image urls
        item['detailed_pic_urls'] = []
        item['detailed_content'] = ''
        content_box_p = article_box.xpath(CONTENT_BOX_FIND_PATENT)
        for each_p in content_box_p:
            # try to get img src
            img_src = each_p.xpath('img/@src').extract_first()
            if img_src:
                item['detailed_pic_urls'].append(img_src)
            else:
                each_text = each_p.xpath('text()').extract_first()
                if len(each_text) > CONTENT_LEN_MIN:
                    # as needed message content
                    # delete strings like <strong>
                    item['detailed_content'] += each_text.strip()
        # filter only needed news
        if re.search(RE_WORDS_FILTER, item['detailed_content']):
            yield item




















