# /html/body/table/tbody/tr/td/div/div[5]/div/div/table
# /html/body/table/tbody/tr/td/div/div[5]/div/div/table[2]
# /html/body/table/tbody/tr/td/div/div[5]/div/div/table[3]


from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from dateutil.parser import parse
from datetime import date
from carib_stockex_scrapers.items import JSEIndexItem,\
    TickerItem, CapValueItem
from dateutil import rrule
from dateutil.rrule import MO, TU, WE, TH, FR


def bdate_range(start, end):
    return rrule.rrule(
        rrule.DAILY,
        byweekday=(MO, TU, WE, TH, FR),
        dtstart=start,
        until=end
    )


def clean_str(instr):
    s = instr.strip()
    s = s.replace(u'\xa0', u'')
    return s.replace(",", "").replace('$', "")


class JSESpider(BaseSpider):

    name = 'jse_equity'
    allowed_domains = ["http://www.jamstockex.com/"]

    def __init__(self, start_date=None, end_date=None):
        if start_date:
            self.start = parse(start_date)
        else:
            self.start = date.today()
        if end_date:
            self.end = parse(end_date)
        else:
            self.end = None

    def start_requests(self):
        domain = "http://www.jamstockex.com"
        controller = "controller.php?action"
        if self.end:
            for dd in bdate_range(start=self.start, end=self.end):
                url = "%s/%s=view_quote&TradingDate=%s" % (
                    domain, controller, dd.strftime("%m/%d/%Y"))
                yield Request(url, self.parse_market_quote)
        else:
            url = "%s/%s=view_quote&TradingDate=%s" % (
                domain, controller, self.start.strftime("%m/%d/%Y")
            )
            yield Request(url, self.parse_market_quote)

    def parse_market_quote(self, response):
        hxs = HtmlXPathSelector(response)
        date_tab = hxs.select('//table')[1]

        dateix = parse(
            " ".join(
            date_tab.select(
            'tr/td/p/text()').extract()[0].split(',')[1:]))

        self.log("Spider Equity Summary for %s" % dateix.strftime(
            "%Y-%m-%d")
        )

        sum_tab = hxs.select('//table')[3]

        jse_market_index = clean_str(
            sum_tab.select('tr')[1].select('td/p/text()')[1].extract())
        jse_market_index_volume = clean_str(
            sum_tab.select('tr')[1].select('td/p/text()')[2].extract())

        jse_select_index = clean_str(
            sum_tab.select('tr')[2].select('td/p/text()')[1].extract())
        jse_select_index_volume = clean_str(
            sum_tab.select('tr')[2].select('td/p/text()')[2].extract())

        jse_composite_index = clean_str(
            sum_tab.select('tr')[3].select('td/p/text()')[1].extract())
        jse_composite_index_volume = clean_str(
            sum_tab.select('tr')[3].select('td/p/text()')[2].extract())
        jse_cross_index = clean_str(
            sum_tab.select('tr')[4].select('td/p/text()')[1].extract())
        jse_cross_index_volume = clean_str(
            sum_tab.select('tr')[4].select('td/p/text()')[2].extract())

        jse_junior_index = clean_str(
            sum_tab.select('tr')[5].select('td/p/text()')[1].extract())

        jse_junior_index_volume = clean_str(
            sum_tab.select('tr')[5].select('td/p/text()')[2].extract())

        jse_combined_index = clean_str(
            sum_tab.select('tr')[6].select('td/p/text()')[1].extract())

        jse_combined_index_volume = clean_str(
            sum_tab.select('tr')[6].select('td/p/text()')[2].extract())

        jse_us_equities_index = clean_str(
            sum_tab.select('tr')[7].select('td/p/text()')[1].extract())

        jse_us_equities_index_volume = clean_str(
            sum_tab.select('tr')[7].select('td/p/text()')[2].extract())

        ji = JSEIndexItem(
            exchange='JSE',
            dateix=dateix.strftime("%Y-%m-%d"),
            jse_market_index=jse_market_index,
            jse_market_index_volume=jse_market_index_volume,
            jse_select_index=jse_select_index,
            jse_select_index_volume=jse_select_index_volume,
            jse_cross_index=jse_cross_index,
            jse_cross_index_volume=jse_cross_index_volume,
            jse_composite_index=jse_composite_index,
            jse_composite_index_volume=jse_composite_index_volume,
            jse_junior_index=jse_junior_index,
            jse_junior_index_volume=jse_junior_index_volume,
            jse_combined_index=jse_combined_index,
            jse_combined_index_volume=jse_combined_index_volume,
            jse_us_equities_index=jse_us_equities_index,
            jse_us_equities_index_volume=jse_us_equities_index_volume
        )

        yield ji
        ord_rows = hxs.select('//table')[4].select('tr')

        for r in range(2, len(ord_rows)):
            ticker = ord_rows[r].select('td')[3].select('p/a').select(
                'text()').extract()[0].strip()
            volume = clean_str(ord_rows[r].select('td')[6].select(
                'p/text()').extract()[0])
            high = clean_str(ord_rows[r].select('td')[7].select(
                'p/text()').extract()[0])
            low = clean_str(ord_rows[r].select('td')[8].select(
                'p/text()').extract()[0])
            open_price = clean_str(ord_rows[r].select('td')[9].select(
                'p/text()').extract()[0])
            close_price = clean_str(ord_rows[r].select('td')[10].select(
                'p/text()').extract()[0])

            ti = TickerItem(
                dateix=dateix.strftime("%y-%m-%d"),
                exchange='JSE',
                ticker=ticker,
                open_price=open_price,
                high_price=high,
                low_price=low,
                close_price=close_price,
                volume=volume)
            yield ti

        pref_rows = hxs.select('//table')[5].select('tr')
        for r in range(2, len(pref_rows)):
            ticker = ord_rows[r].select('td')[3].select('p/a').select(
                'text()').extract()[0].strip()
            volume = clean_str(ord_rows[r].select('td')[6].select(
                'p/text()').extract()[0])
            high = clean_str(ord_rows[r].select('td')[7].select(
                'p/text()').extract()[0])
            low = clean_str(ord_rows[r].select('td')[8].select(
                'p/text()').extract()[0])
            open_price = clean_str(ord_rows[r].select('td')[9].select(
                'p/text()').extract()[0])
            close_price = clean_str(ord_rows[r].select('td')[10].select(
                'p/text()').extract()[0])

            ti = TickerItem(
                dateix=dateix.strftime("%y-%m-%d"),
                exchange='JSE',
                ticker=ticker,
                open_price=open_price,
                high_price=high,
                low_price=low,
                close_price=close_price,
                volume=volume)
            yield ti
