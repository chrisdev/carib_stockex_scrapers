# Scrapy settings for carib_stockex_scrapers project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#


#BOT_NAME = 'carib_stockex_scrapers'
#BOT_VERSION = '1.0'
TELNETCONSOLE_ENABLED = False

ITEM_PIPELINES = {
    'carib_stockex_scrapers.pipelines.DjangoLoaderPipeline': 1
}
SPIDER_MODULES = ['carib_stockex_scrapers.spiders']
NEWSPIDER_MODULE = 'carib_stockex_scrapers.spiders'
#USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
