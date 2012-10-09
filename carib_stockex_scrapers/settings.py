# Scrapy settings for carib_stockex_scrapers project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#


def setup_django_env(path):
    import imp
    import sys
    from os.path import join
    from django.core.management import setup_environ

    f, filename, desc = imp.find_module('settings', [path])
    project = imp.load_module('settings', f, filename, desc)

    setup_environ(project)

    sys.path.insert(0, PATH_TO_DJANGO_PROJECT)
    sys.path.insert(0, join(PATH_TO_DJANGO_PROJECT, "apps"))


BOT_NAME = 'carib_stockex_scrapers'
BOT_VERSION = '1.0'
TELNETCONSOLE_ENABLED = False

ITEM_PIPELINES = [
    'carib_stockex_scrapers.pipelines.DjangoLoaderPipeline',
]
SPIDER_MODULES = ['carib_stockex_scrapers.spiders']
NEWSPIDER_MODULE = 'carib_stockex_scrapers.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

PATH_TO_DJANGO_PROJECT = '/Users/cclarke/Development/mass_site'

setup_django_env(PATH_TO_DJANGO_PROJECT)
