from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from dateutil.parser import parse
from datetime import date
from scrapy import log
from carib_stockex_scrapers.items import MarketSummaryItem,TickerItem


def clean_str(instr):
    s=instr.strip()
    s=s.replace(u'\xa0',u'')
    return s.replace(",","").replace('$',"")

class TTSESpider(BaseSpider):
    name = 'ttse'
    allowed_domains=["http://www.stockex.co.tt"]

    def __init__(self,dateix=None):
        #import ipdb; ipdb.set_trace()
        if dateix:
            self.dd=parse(dateix)
        else:
            self.dd=date.today()
    
        self.start_urls = [
              "http://www.stockex.co.tt/controller.php?action=view_quote&TradingDate=%s" % self.dd.strftime("%m/%d/%y")
              ]

    def parse(self,response):
        self.log("processing results for %s" % self.dd)
        hxs = HtmlXPathSelector(response)
        item_list=[]

        
        sum_tab=hxs.select('//table')[3]
        composite_ix=clean_str(sum_tab.select('tr')[1].select('td/p/text()')[1].extract())
        total_volume=clean_str(sum_tab.select('tr')[1].select('td/p/text()')[4].extract())
        total_value=clean_str(sum_tab.select('tr')[1].select('td/p/text()')[5].extract())
        num_trades=clean_str(sum_tab.select('tr')[1].select('td/p/text()')[6].extract())

        alltt_ix=clean_str(sum_tab.select('tr')[2].select('td/p/text()')[1].extract())
        tt_volume=clean_str(sum_tab.select('tr')[2].select('td/p/text()')[4].extract())
        tt_value=clean_str(sum_tab.select('tr')[2].select('td/p/text()')[5].extract())
        tt_trades=clean_str(sum_tab.select('tr')[2].select('td/p/text()')[6].extract())

        cross_ix=clean_str(sum_tab.select('tr')[3].select('td/p/text()')[1].extract())
        cross_volume=clean_str(sum_tab.select('tr')[3].select('td/p/text()')[4].extract())
        cross_value=clean_str(sum_tab.select('tr')[3].select('td/p/text()')[5].extract())
        cross_trades=clean_str(sum_tab.select('tr')[3].select('td/p/text()')[6].extract())

        yield MarketSummaryItem(
            exchange='TTSE',
            dateix =self.dd,
            composite_ix= composite_ix,
            total_market_volume=total_volume,
            total_market_value=total_value,
            total_trades=num_trades,
            alltt_ix=alltt_ix,
            tt_volume =tt_volume,
            tt_value =tt_value,
            tt_trades =tt_trades,
            cross_ix =cross_ix,
            cross_volume =cross_volume,
            cross_value =cross_value,
            cross_trades =cross_trades
            )

        
         


        self.log("%s composite_ix:%s total_volume:%s total_value %s num_trades %s" % (
                  self.dd,composite_ix,total_volume,total_value,num_trades)
                )
        
        ord_rows=hxs.select('//table')[4].select('tr')
        #data_cols=[2,3,4,5,12,11]
        #col_names=['open_price','high_price','low_price','close_price','volume']
        for r in range(2,len(ord_rows)):
            ticker = ord_rows[r].select('td')[1].select('p/a').select('text()').extract()[0].strip()
            details_url = clean_str(ord_rows[r].select('td')[1].select('p/a').select('@href').extract()[0])
            open_price=clean_str(ord_rows[r].select('td')[2].select('p/text()').extract()[0])
            high_price=clean_str(ord_rows[r].select('td')[3].select('p/text()').extract()[0])
            low_price=clean_str(ord_rows[r].select('td')[4].select('p/text()').extract()[0])
            volume=clean_str(ord_rows[r].select('td')[11].select('p/text()').extract()[0])
            close_price=clean_str(ord_rows[r].select('td')[12].select('p/text()').extract()[0])
            
            self.log("%s ticker:%s open:%s high %s low %s close %s volume: %s" % (
                  self.dd.strftime("%m/%d/%y"),
                  ticker,open_price,high_price,low_price,close_price,volume)
                )
            yield TickerItem(dateix=self.dd,
                             exchange='TTSE', 
                             ticker=ticker,
                             open_price=open_price,
                             high_price=high_price,
                             low_price=low_price,
                             close_price=close_price,
                             volume=volume)

            
