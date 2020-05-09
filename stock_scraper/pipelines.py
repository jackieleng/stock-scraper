import pymongo

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class StockScraperPipeline:
    def process_item(self, item, spider):
        return item


class MongoPipeline:
    def __init__(
        self, mongo_uri: str, mongo_db: str, mongo_collection_name: str = None
    ):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection_name = mongo_collection_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get(
                "MONGO_URI", "mongodb://localhost:27017"
            ),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "scrapy"),
            mongo_collection_name=crawler.settings.get(
                "MONGO_COLLECTION_NAME"
            ),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        coll_name = (
            self.mongo_collection_name
            if self.mongo_collection_name
            else spider.name
        )
        self.db[coll_name].replace_one(
            {"ticker": item["ticker"]}, dict(item), upsert=True
        )
        return item
