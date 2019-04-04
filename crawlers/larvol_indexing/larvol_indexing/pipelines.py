# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pprint import pprint
from larvol_indexing import my_database

class LarvolIndexingPipeline(object):

    def getMonth(self, val):
        if val == 1:
            return "January"
        elif val == 2:
            return "February"
        elif val == 3:
            return "March"
        elif val == 4:
            return "April"
        elif val == 5:
            return "May"
        elif val == 6:
            return "June"
        elif val == 7:
            return "July"
        elif val == 8:
            return "August"
        elif val == 9:
            return "September"
        elif val == 10:
            return "October"
        elif val == 11:
            return "November"
        elif val == 12:
            return "December"
        else:
            return ""
    def process_item(self, item, spider):
        if spider.name == 'esmo':
            session_id = ""
            url = item['url']
            session_title = item['session_title']
            session_title = " ".join(session_title)
            if "ID" in session_title:
                session_id = session_title.split("(ID")[1].split(")")[0].strip()
                make_false_id = "(ID {})".format(session_id)
                article_title = session_title.replace(make_false_id," ").strip()
            else:
                article_title = session_title


            location = item['location']
            date = item['date']


            time = item['time']
            chairs = item['chairs']
            chairs_affiliations = item['chairs_affiliations']
            session_type = item['session_type']
            presentation_data = item['presentation_data']
            crawl_id = item['crawl_id']
            month_name = self.getMonth(int(date.split(".")[1].strip()))
            date ="{} {}, {}".format(month_name, date.split(".")[0], date.split(".")[2])
            start_time = time.split("-")[0].strip()
            end_time = time.split("-")[1].strip()

            data_dict = {
                "source_id": "",
                "session_id":session_id,
                "crawl_id": crawl_id,
                "session_title": session_title.replace("\n"," ").strip(),
                "article_title": article_title.replace("\n"," ").strip(),
                "start_time": start_time,
                "end_time": end_time,
                "date": date,
                "session_type": session_type,
                "chairs": chairs,
                "authors": "",
                "authors_affiliations":"",
                "chairs_affiliations": chairs_affiliations,
                "location": location,
                "url": url,
            }
            pprint(data_dict)
            my_database.crawled_data.insert_one(data_dict)

            for data in presentation_data:
                article_title = data['article_title']
                if "ID" in article_title:
                    source_id = article_title.split("(ID")[1].split(")")[0].strip()
                    make_false_id = "(ID {})".format(source_id)
                    article_title = article_title.replace(make_false_id," ").strip()
                presentation_time = data['presentation_time'].strip()
                if presentation_time != '':
                    start_time = presentation_time.split("-")[0].strip()
                    end_time = presentation_time.split("-")[1].strip()
                authors = data['authors']
                authors_affiliations = data['authors_affiliations']
                data_dict = {
                    "source_id": source_id,
                    "session_id":'',
                    "crawl_id": crawl_id,
                    "session_title": session_title.replace("\n"," ").strip(),
                    "article_title": article_title,
                    "start_time": start_time,
                    "end_time": end_time,
                    "date": date,
                    "session_type": session_type,
                    "chairs": '',
                    "authors": authors,
                    "authors_affiliations": authors_affiliations,
                    "chairs_affiliations": '',
                    "location": location,
                    "url": url,
                }
                pprint(data_dict)
                my_database.crawled_data.insert_one(data_dict)




        return item
