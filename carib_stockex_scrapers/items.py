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
    total_number_trades = Field()


class JSEIndexItem(Item):
    exchange = Field()
    dateix = Field()
    jse_market_index = Field()
    jse_market_index_volume = Field()
    jse_select_index = Field()
    jse_select_index_volume = Field()
    jse_composite_index = Field()
    jse_cross_index = Field()
    jse_cross_index_volume = Field()
    jse_composite_index_volume = Field()
    jse_junior_index = Field()
    jse_junior_index_volume = Field()
    jse_combined_index = Field()
    jse_combined_index_volume = Field()
    jse_us_equities_index = Field()
    jse_us_equities_index_volume = Field()


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
    total_number_trades = Field()


class MarketCapValueItem(Item):
    exchange = Field()
    dateix = Field()
    capital_value = Field()
    trade_count = Field()
    traded_value = Field()


class BondListingItem(Item):
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


class EquityItem(Item):
    company_name = Field()
    symbol = Field()
    financial_year_end = Field()
    status = Field()
