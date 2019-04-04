from pymongo import MongoClient

client = MongoClient()
db = client.LARVOL_CLOUD
crawl_initiate = db.CRAWLING_INITIATES
crawled_data = db.CRAWLED_DATA
