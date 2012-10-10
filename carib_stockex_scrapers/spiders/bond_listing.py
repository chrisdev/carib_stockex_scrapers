from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from carib_stockex_scrapers.items import BondListingItems
from datetime import date


class TTBondListingSpider(CrawlSpider):
    name = 'ttse_bond_listing'
    allowed_domains = ['stockex.co.tt']
    start_urls = [
        'http://www.stockex.co.tt/controller.php?action=listed_bonds'
    ]

    def parse_item(self):
        hxs = HtmlXPathSelector(self)
        data_rows = hxs.select('//table')[0].select('tr')
        item_args = {}
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

        for r in data_map:
            item_args[r[1]] = data_rows[r[0]].select(
                'td')[1].select('text()').extract()[0].strip()
        item_args['exchange'] = 'TTSE'
        item_args['dateix'] = date.today().strftime("%y-%m-%d")
        yield BondListingItems(**item_args)
    rules = (
        Rule(SgmlLinkExtractor(allow=(r'StockCode=\d+')), callback=parse_item),
    )
