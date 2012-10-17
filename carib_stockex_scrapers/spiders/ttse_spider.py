from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from dateutil.parser import parse
from datetime import date
from carib_stockex_scrapers.items import MarketSummaryItem,\
    TickerItem, CapValueItem
from dateutil import rrule
from dateutil.rrule import MO, TU, WE, TH, FR


def clean_str(instr):
    s = instr.strip()
    s = s.replace(u'\xa0', u'')
    return s.replace(",", "").replace('$', "")


def bdate_range(start, end):
    return rrule.rrule(
        rrule.DAILY,
        byweekday=(MO, TU, WE, TH, FR),
        dtstart=start,
        until=end
    )


class TTSESpider(BaseSpider):
    name = 'ttse_equity'
    allowed_domains = ["http://www.stockex.co.tt"]

    def __init__(self, start_date=None, end_date=None):
        #super(TTSESpider, self).__init__(name, **kwargs)
        #import ipdb; ipdb.set_trace()
        if start_date:
            self.start = parse(start_date)
        else:
            self.start = date.today()
        if end_date:
            self.end = parse(end_date)
        else:
            self.end = None

    def start_requests(self):
        domain = "http://www.stockex.co.tt"
        controller = "controller.php?action"
        if self.end:
            for dd in bdate_range(start=self.start, end=self.end):
                url = "%s/%s=view_quote&TradingDate=%s" % (
                    domain, controller, dd.strftime("%m/%d/%Y"))
                yield Request(url, self.parse_equity_summary)

                url = "%s/%s=view_daily_index_summary&TradingDate=%s" % (
                    domain, controller, dd.strftime("%m/%d/%Y"))
                yield Request(url, self.parse_index_summary)
        else:
            url = "%s/%s=view_quote&TradingDate=%s" % (
                domain, controller, self.start.strftime("%m/%d/%Y")
            )
            yield Request(url, self.parse_equity_summary)
            url = "%s/%s=view_daily_index_summary&TradingDate=%s" % (
                domain, controller, self.start.strftime("%m/%d/%Y")
            )
            yield Request(url, self.parse_index_summary)

    def parse_index_summary(self, response):
        hxs = HtmlXPathSelector(response)
        date_tab = hxs.select('//table')[1]
        dateix = parse(
            " ".join(
            date_tab.select(
            'tr/td/p/text()').extract()[0].split(',')[1:]))

        self.log("Spider Index Summary for %s" % dateix.strftime(
            "%Y-%m-%d")
        )
        data_rows = hxs.select('//table')[2].select('tr')
        for r in range(1, len(data_rows)):
            try:
                ticker = data_rows[r].select('td')[0].select(
                    'p/a').select(
                        'text()'
                    ).extract()[0].strip()

            except IndexError:
                continue
            issued_capital = clean_str(data_rows[r].select('td')[1].select(
                'p/text()').extract()[0])
            captial_value = clean_str(data_rows[r].select('td')[2].select(
                'p/text()').extract()[0])
            trade_count = clean_str(data_rows[r].select('td')[3].select(
                'p/text()').extract()[0])
            traded_value = clean_str(data_rows[r].select('td')[4].select(
                'p/text()').extract()[0])
            yield CapValueItem(
                exchange='TTSE',
                dateix=dateix.strftime("%Y-%m-%d"),
                ticker=ticker,
                issued_capital=issued_capital,
                capital_value=captial_value,
                trade_count=trade_count,
                traded_value=traded_value)

    def parse_equity_summary(self, response):
        hxs = HtmlXPathSelector(response)
        #from scrapy.shell import inspect_response
        #inspect_response(response)
        date_tab = hxs.select('//table')[1]
        dateix = parse(
            " ".join(
            date_tab.select(
            'tr/td/p/text()').extract()[0].split(',')[1:]))
        self.log("Spider Equity Summary for %s" % dateix.strftime(
            "%Y-%m-%d")
        )
        sum_tab = hxs.select('//table')[3]
        composite_ix = clean_str(
            sum_tab.select('tr')[1].select('td/p/text()')[1].extract())
        total_volume = clean_str(
            sum_tab.select('tr')[1].select('td/p/text()')[4].extract())
        total_value = clean_str(
            sum_tab.select('tr')[1].select('td/p/text()')[5].extract())
        num_trades = clean_str(
            sum_tab.select('tr')[1].select('td/p/text()')[6].extract())

        alltt_ix = clean_str(
            sum_tab.select('tr')[2].select('td/p/text()')[1].extract())
        tt_volume = clean_str(
            sum_tab.select('tr')[2].select('td/p/text()')[4].extract())
        tt_value = clean_str(
            sum_tab.select('tr')[2].select('td/p/text()')[5].extract())
        tt_trades = clean_str(
            sum_tab.select('tr')[2].select('td/p/text()')[6].extract())

        cross_ix = clean_str(
            sum_tab.select('tr')[3].select('td/p/text()')[1].extract())
        cross_volume = clean_str(
            sum_tab.select('tr')[3].select('td/p/text()')[4].extract())
        cross_value = clean_str(
            sum_tab.select('tr')[3].select('td/p/text()')[5].extract())
        cross_trades = clean_str(
            sum_tab.select('tr')[3].select('td/p/text()')[6].extract())
        yield MarketSummaryItem(
            exchange='TTSE',
            dateix=dateix.strftime("%Y-%m-%d"),
            composite_ix=composite_ix,
            total_market_volume=total_volume,
            total_market_value=total_value,
            total_trades=num_trades,
            alltt_ix=alltt_ix,
            tt_volume=tt_volume,
            tt_value=tt_value,
            tt_trades=tt_trades,
            cross_ix=cross_ix,
            cross_volume=cross_volume,
            cross_value=cross_value,
            cross_trades=cross_trades
        )
        log_str = "%s composite_ix:%s volume:%s value %s num_trades %s"
        self.log(
            log_str % (
                dateix, composite_ix, total_volume,
                total_value, num_trades)
        )
        log_str = "%s ticker:%s open:%s high %s low %s close %s volume: %s"
        for t in [4, 5, 6]:
            ord_rows = hxs.select('//table')[t].select('tr')
            for r in range(2, len(ord_rows)):
                ticker = ord_rows[r].select('td')[1].select(
                    'p/a').select(
                        'text()').extract()[0].strip()
                open_price = clean_str(ord_rows[r].select(
                    'td')[2].select(
                        'p/text()').extract()[0])
                high_price = clean_str(ord_rows[r].select('td')[3].select(
                    'p/text()').extract()[0])
                low_price = clean_str(ord_rows[r].select('td')[4].select(
                    'p/text()').extract()[0])
                volume = clean_str(ord_rows[r].select('td')[11].select(
                    'p/text()').extract()[0])
                close_price = clean_str(ord_rows[r].select('td')[12].select(
                    'p/text()').extract()[0])

                self.log(log_str % (
                    dateix.strftime("%m/%d/%y"), ticker,
                    open_price, high_price,
                    low_price, close_price, volume)
                )
                yield TickerItem(dateix=dateix.strftime("%Y-%m-%d"),
                                 exchange='TTSE',
                                 ticker=ticker,
                                 open_price=open_price,
                                 high_price=high_price,
                                 low_price=low_price,
                                 close_price=close_price,
                                 volume=volume)
