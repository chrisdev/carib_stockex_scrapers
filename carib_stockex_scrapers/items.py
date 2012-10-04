# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class CaribStockexScrapersItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class MarketSummaryItem(Item):
    exchange=Field()
    dateix=Field()
    composite_ix=Field()
    total_market_volume=Field()
    total_market_value = Field()
    total_trades = Field()
    alltt_ix=Field()
    tt_volume=Field()
    tt_value = Field()
    tt_trades = Field()
    cross_ix=Field()
    cross_volume=Field()
    cross_value = Field()
    cross_trades = Field()	


class TickerItem(Item):
    exchange=Field()
    dateix=Field()
    ticker=Field()
    open_price=Field()
    high_price=Field()
    low_price=Field()
    close_price=Field()
    volume=Field()

class SymbolShares(Item):
    exchange=Field()
    dateix=Field()
    ticker=Field()
    shares_outstanding=Field()
    maket_cap=Field()
		