# Scrapy settings for a project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import os
import yaml

BOT_NAME = 'sipper'

SPIDER_MODULES = ['sipper.spiders']
NEWSPIDER_MODULE = 'sipper.spiders'

ITEM_PIPELINES = {
    'sipper.pipelines.AlreadyDownloadedFilter': 300,
    'sipper.pipelines.DownloadPipeline': 500,
}

# load the credentials
AUTH_FILE = os.path.join(os.path.dirname(__file__), '..', 'auth.yml')

with open(AUTH_FILE) as f:
    CREDENTIALS = yaml.load(f.read())


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'a (+http://www.yourdomain.com)'
