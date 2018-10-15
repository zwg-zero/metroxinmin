# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MetroNewsItem(scrapy.Item):
    title = scrapy.Field()
    datetime = scrapy.Field()
    summary_pic_url = scrapy.Field()
    summary_content = scrapy.Field()
    source_tags = scrapy.Field()  # format like: 新民头条-新民突发
    source = scrapy.Field()  # format like: 新民晚报
    journalist = scrapy.Field()
    editor = scrapy.Field()
    detailed_content = scrapy.Field()
    detailed_pic_urls = scrapy.Field()
