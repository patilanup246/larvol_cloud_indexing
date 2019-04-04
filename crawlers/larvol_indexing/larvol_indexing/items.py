# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ESMOITEMS(scrapy.Item):
    url = scrapy.Field()
    session_title = scrapy.Field()
    location = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    chairs = scrapy.Field()
    chairs_affiliations = scrapy.Field()
    session_type = scrapy.Field()
    presentation_data = scrapy.Field()
    crawl_id = scrapy.Field()
