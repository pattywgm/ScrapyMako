# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import datetime
import socket
import scrapy
import hashlib
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
count = 0
today = datetime.date.today().strftime('%Y%m%d')


class ImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url.strip())

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('${project.spider.result_dir}/${project.spider.name}_{}.json'.format(today), 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        result = {
            'meta_version': spider.meta_version,
            'meta_updated': datetime.datetime.now().isoformat()[:19],
            'download_config': {
                'url': item["url"],
                'method': 'GET'
            },
            'download_data': {
                'parsed_data': {},
                'raw_data': {},
            }
        }

        for k in item.keys():
            if k == "url":
                continue
            result['download_data']['parsed_data'][k] = item[k]
        self.file.write(json.dumps(result, ensure_ascii=False).encode('utf-8') + '\n')
        return item


class CsvWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('${project.spider.name}_{}.csv'.format(today), 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = "\t".join(dict(item).values())
        self.file.write(line.encode('utf-8'))
        return item


class MongoPipeline(object):

    def open_spider(self, spider):
        import pymongo
        host = spider.settings.get('MONGODB_HOST')
        port = spider.settings.get('MONGODB_PORT')
        db_name = spider.settings.get('MONGODB_DBNAME')
        client = pymongo.MongoClient(host=host, port=port)
        db = client[db_name]
        self.collection = db[spider.settings.get('MONGODB_DOCNAME')]

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item



class ElasticSearchPipeline(object):

    def __init__(self):
        from pyes import ES
        self.settings = get_project_settings()
        if self.settings['ELASTICSEARCH_PORT']:
            uri = "%s:%d" % (self.settings['ELASTICSEARCH_SERVER'], self.settings['ELASTICSEARCH_PORT'])
        else:
            uri = "%s" % (self.settings['ELASTICSEARCH_SERVER'])
        self.es = ES([uri])

    def process_item(self, item, spider):
        if self.__get_uniq_key() is None:
            self.es.index(dict(item), self.settings['ELASTICSEARCH_INDEX'], self.settings['ELASTICSEARCH_TYPE'],
                          id=item['id'], op_type='create',)
        else:
            self.es.index(dict(item), self.settings['ELASTICSEARCH_INDEX'], self.settings['ELASTICSEARCH_TYPE'],
                          self._get_item_key(item))
        return item

    def _get_item_key(self, item):
        uniq = self.__get_uniq_key()
        if isinstance(uniq, list):
            values = [item[key] for key in uniq]
            value = ''.join(values)
        else:
            value = uniq

        return hashlib.sha1(value).hexdigest()

    def __get_uniq_key(self):
        if not self.settings['ELASTICSEARCH_UNIQ_KEY'] or self.settings['ELASTICSEARCH_UNIQ_KEY'] == "":
            return None
        return self.settings['ELASTICSEARCH_UNIQ_KEY']
