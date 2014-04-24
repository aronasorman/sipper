import logging
import os
import urlparse

from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from scrapy.spider import Spider

from sipper import settings
from sipper.items import Screencast


class ScreencastSpider(Spider):
    name = "screencast"
    allowed_domains = ["elixirsips.dpdcart.com"]
    start_urls = ["https://elixirsips.dpdcart.com/subscriber/content"]

    def parse(self, response):
        return [
            FormRequest.from_response(
                response,
                formdata={
                    'username': settings.USERNAME,
                    'password': settings.PASSWORD,
                },
            callback=self.after_login,
            )]


    def after_login(self, response):
        if "password" in response.body:
            self.log("Login failed.", level=logging.ERROR)
            return
        else:
            self.log("Login successful", level=logging.DEBUG)

        # valid login code path

        # extract the root url and scheme for concatenating with links we find
        u = urlparse.urlparse(response.url)
        self.root_url = "%(scheme)s://%(netloc)s" % {'scheme': u.scheme, 'netloc': u.netloc}

        sel = Selector(response)
        screencast_entries = sel.xpath('//div[@class="content-post-meta"]')
        items = []
        for entry in screencast_entries:
            detail_link = entry.xpath('span/a/@href').extract()[0]
            detail_link = self.root_url + detail_link
            items.append(Request(detail_link,
                                 callback=self.parse_screencast_detail))
        return items


    def parse_screencast_detail(self, response):
        self.log("Parsing %s" % response.url, level=logging.INFO)

        item = Screencast()
        sel = Selector(response)
        potential_video_nodes = sel.xpath('//ul/li')
        for node in potential_video_nodes:
            entry_name = node.xpath('a/text()').extract()
            if not entry_name or not'.mp4' in entry_name[0]:
                continue
            else:
                item['video'] = self.root_url + node.xpath('a/@href').extract()[0]
                item['title'] = sel.xpath('//div[@class="section-header order"]/h2/text()').extract()[0]
                break

        # download video, it we haven't already
        dlpath = settings.DOWNLOAD_PATH
        video_path = os.path.join(dlpath, item.video_name())
        if os.path.exists(video_path):
            self.log("%s already downloaded" % item['title'])
            return item
        else:
            request = Request(item['video'], callback=self.video_downloaded)
            request.meta['item'] = item
            return request


    def video_downloaded(self, response):
        dlpath = settings.DOWNLOAD_PATH
        item = response.meta['item']
        video_path = os.path.expanduser(os.path.join(dlpath, item.video_name()))

        if not os.path.exists(dlpath):
            os.makedirs(dlpath)

        with open(video_path, 'w') as f:
            f.write(response.body)
        spider.log('Successfully downloaded to %s' % video_path)

        return item
