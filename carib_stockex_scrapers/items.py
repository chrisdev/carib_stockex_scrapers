# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class MarketSummaryItem(Item):
    exchange = Field()
    dateix = Field()
    composite_ix = Field()
    total_market_volume = Field()
    total_market_value = Field()
    total_trades = Field()
    alltt_ix = Field()
    tt_volume = Field()
    tt_value = Field()
    tt_trades = Field()
    cross_ix = Field()
    cross_volume = Field()
    cross_value = Field()
    cross_trades = Field()


class TickerItem(Item):
    exchange = Field()
    dateix = Field()
    ticker = Field()
    open_price = Field()
    high_price = Field()
    low_price = Field()
    close_price = Field()
    volume = Field()


class CapValueItem(Item):
    exchange = Field()
    dateix = Field()
    ticker = Field()
    issued_capital = Field()
    capital_value = Field()
    trade_count = Field()
    traded_value = Field()

class BondListingItems(Item):
    exchange = Field()
    dateix = Field()
    symbol = Field()
    isin = Field()
    bond_type = Field()
    security_name = Field()
    short_name = Field()
    issuer = Field()
    description = Field()
    address = Field()
    url = Field()
    issue_date = Field()
    maturity_date = Field()
    coupon_rate = Field()
    face_value = Field()
    par_value = Field()
    rate_type = Field()
    currency = Field()
    country = Field()
    status = Field()
