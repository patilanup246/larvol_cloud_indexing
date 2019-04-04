# -*- coding: utf-8 -*-
import scrapy
from larvol_indexing.items import ESMOITEMS
from larvol_indexing import my_database
from bs4 import BeautifulSoup
from datetime import datetime
from strgen import StringGenerator as SG
from scrapy import signals

class EsmoSpider(scrapy.Spider):
    name = 'esmo'
    allowed_domains = ['ctimeetingtech.com']
    start_urls = [
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=1',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=2',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=3',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=4',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=5',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=6',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=7',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=8',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=9',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=10',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=11',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=12',
        'https://cslide.ctimeetingtech.com/esmo2019/attendee/confcal/session/list?p=13',

    ]

    def __init__(self, category=None, *args, **kwargs):
        super(EsmoSpider, self).__init__(*args, **kwargs)
        unique_id = SG("[\l\d]{10}").render()
        date_object = str(datetime.now().day)+str(datetime.now().month)+str(datetime.now().year)
        date_object = str(date_object)+"_"+str(datetime.now().time()).replace(":","_").split(".")[0]
        unique_id = date_object + "_"+unique_id
        unique_id = unique_id.replace(" ","_").strip()
        self.CRAWL_NEW_ID = unique_id
        data_dict = {
            "crawl_id": self.CRAWL_NEW_ID,
            "conf":"esmo",
            "start_datetime": datetime.now(),
            "end_datetime":"",
            "status": "running",
        }
        my_database.crawl_initiate.insert_one(data_dict)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(EsmoSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider


    def spider_closed(self, spider):
        my_database.crawl_initiate.update_many({
                  'crawl_id': self.CRAWL_NEW_ID,
                },{
                  '$set': {'status':'completed','end_datetime': datetime.now(),}
                }, upsert=False)
        spider.logger.info('Spider closed: %s', spider.name)


    def parse(self, response):
        for href in response.xpath("//h4/a/@href"):
            href = response.urljoin(href.extract())
            yield scrapy.Request(href, callback=self.parse_session)

    def parse_session(self, response):

        all_presentation_data = []
        html_content = response.body
        soup = BeautifulSoup(html_content, 'lxml')

        for data in soup.findAll('div', {'class':'card presentation'}):
            html_con = str(data)
            article_title = data.find('h4').text
            timee = html_con.split("Lecture Time")[1].split("</div>")[0].split("</span>")[0].replace('">','').strip()
            authors = []
            authors_affiliations = []
            auth_object = data.find('ul',{'class':'persons'})
            if auth_object is not None:
                for auth_data in auth_object.findAll('li'):
                    auu = auth_data.text
                    auu = auu.split("(")[0].strip()
                    authors.append(auu)
                    aff_data = auth_data.find('small').text
                    aff_data = aff_data.replace("("," ").replace(")"," ").strip()
                    authors_affiliations.append(aff_data)
            authors = "| ".join(authors)
            authors_affiliations = "| ".join(authors_affiliations).strip()


            data_dict = {
                "article_title": article_title,
                "presentation_time": timee,
                "authors": authors,
                "authors_affiliations": authors_affiliations,
            }
            all_presentation_data.append(data_dict)
        chairs = response.xpath("//div[@class='property-container internal_moderators']//ul[@class='persons']/li/text()").extract()
        chairs_affiliations = response.xpath("//div[@class='property-container internal_moderators']//ul[@class='persons']/li/small/text()").extract()
        chairs = "| ".join(chairs).strip()
        chairs_affiliations = "| ".join(chairs_affiliations).replace("("," ").replace(")"," ").strip()
        item = ESMOITEMS()
        item['session_title'] = response.xpath("//h4[@class='session-title card-title']//text()").extract()
        item['location'] = response.xpath("//div[text()='Location']/following-sibling::div/text()").extract_first()
        item['date'] = response.xpath("//div[text()='Date']/following-sibling::div/text()").extract_first()
        item['time'] = response.xpath("//div[text()='Time']/following-sibling::div/text()").extract_first()
        item['chairs'] = chairs
        item['chairs_affiliations'] = chairs_affiliations
        item['session_type'] = response.xpath("//span[@title='Session Type']/text()").extract_first()
        item['presentation_data'] = all_presentation_data
        item['url'] = response.url
        item['crawl_id'] = self.CRAWL_NEW_ID
        yield item
