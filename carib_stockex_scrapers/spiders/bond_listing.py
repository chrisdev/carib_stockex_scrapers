from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from carib_stockex_scrapers.items import BondListingItem
from datetime import date
from scrapy.stats import stats
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy import log

class TTBondListingSpider(CrawlSpider):
    name = 'ttse_bond_listing'
    allowed_domains = ['stockex.co.tt']
    start_urls = [
        'http://www.stockex.co.tt/controller.php?action=listed_bonds'
    ]
    failed = []
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'StockCode=\d+')),
             callback='parse_item'),
    )


    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        data_rows = hxs.select('//table')[0].select('tr')
        item_kwargs = {}
        data_map = [
            (0, "symbol"),
            (1, "isin"),
            (2, "bond_type"),
            (3, "security_name"),
            (4, "short_name"),
            (5, "issuer"),
            (6, "description"),
            (7, "address"),
            (8, "url"),
            (9, "issue_date"),
            (10, "maturity_date"),
            (11, "coupon_rate"),
            (12, "face_value"),
            (13, "par_value"),
            (14, "rate_type"),
            (15, "currency"),
            (16, "country"),
            (17, "status"),
        ]

        for ro in data_map:
            try:
                item_kwargs[ro[1]] = data_rows[ro[0]].select(
                    'td')[1].select('text()').extract()[0].strip()
            except IndexError:
                data_str = ' '.join([x.extract().strip()
                       for x in data_rows.select('td').select('text()')])
                log.msg('ERRROR: {0}\n{1}'.format(response.url,data_str))
                self.failed.append('{0}\n{1}'.format(response.url,data_str))
                stats.inc_value('failed_item_count')
                return
        item_kwargs['exchange'] = 'TTSE'
        item_kwargs['dateix'] = date.today().strftime("%y-%m-%d")
        bond = BondListingItem(**item_kwargs)
        yield bond

        def handle_spider_closed(spider, reason):
            stats.set_value('failed items', '\n'.join(spider.failed))

        dispatcher.connect(handle_spider_closed, signals.spider_closed)

