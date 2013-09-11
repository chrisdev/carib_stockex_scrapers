from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from carib_stockex_scrapers.items import EquityItem
from scrapy.item import Item

def clean_str(instr):
    s = instr.strip()
    s = s.replace(u'\xa0', u'')
    return s.replace(",", "").replace('$', "")


class TTEquityListingSpider(CrawlSpider):
    name = 'ttse_equity_listing'
    allowed_domains = ['stockex.co.tt']
    start_urls = [
        'http://www.stockex.co.tt/controller.php?action=listed_companies'
    ]

    def parse_item(self, response):

        hxs = HtmlXPathSelector(response)
        tabs = hxs.select('//table')
        company = clean_str(
            tabs[1].select('tr')[1].select('td/text()').extract()[0]
        )
        symbol = clean_str(
            tabs[1].select('tr')[2].select('td/text()').extract()[0]
        )
        financial_year_end = clean_str(
            tabs[1].select('tr')[5].select('td/text()').extract()[0]
        )

        status = clean_str(
            tabs[1].select('tr')[3].select('td/text()').extract()[0]
        )


        equity = EquityItem(company_name=company, symbol=symbol,
                          financial_year_end=financial_year_end,
                          status=status)

        return equity

    rules = (Rule(SgmlLinkExtractor(allow='view_stock_chart'),
                  callback='parse_item'),)
