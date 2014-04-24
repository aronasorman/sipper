# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Screencast(Item):
    title = Field()
    video = Field()


    def video_name(self):
        return "%s.mp4" % self['title']
