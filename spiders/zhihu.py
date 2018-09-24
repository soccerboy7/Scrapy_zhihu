# -*- coding: utf-8 -*-
import json

from scrapy import Request,Spider

from zhihuuser.items import ZhihuuserItem


class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com/']
    start_urls = ['https://www.zhihu.com//']
    start_user = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    def start_requests(self):
        yield Request(self.user_url.format(user = self.start_user,include = self.user_query),callback=self.parse_user,dont_filter=True) #官方对这个的解释，是你要request的地址和allow_domain里面的冲突，从而被过滤掉。可以停用过滤功能。
        yield Request(self.follows_url.format(user=self.start_user, include=self.follows_query,offset=0,limit=20), callback=self.parse_follows,dont_filter=True)

    def parse_user(self, response):
        result = json.loads(response.text) # 将爬来的数据解析成为json格式
        item = ZhihuuserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

    def parse_follows(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user = result['url_token'],include = self.user_query),callback=self.parse_user,dont_filter=True)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,callback=self.parse_follows,dont_filter=True)
