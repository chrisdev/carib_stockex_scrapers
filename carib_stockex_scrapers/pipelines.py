# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy import log
from markets.models import Symbol, Exchange, SymbolData, MarketSummary,\
    ShareIssue
from trading.models import Security, InstrumentType
from carib_stockex_scrapers.items import (
    BondListingItem, MarketSummaryItem, JSEIndexItem,
    TickerItem, CapValueItem, EquityItem, MarketCapValueItem)
from dateutil.parser import parse
from django.utils.timezone import get_current_timezone, make_aware
from datetime import datetime
from scrapy.stats import stats


class DjangoLoaderPipeline(object):

    def to_float(self, instr):
        try:
            return(float(instr))
        except (ValueError, TypeError, AttributeError):
            return None

    def spider_closed(self, spider):
        log.msg("Processed {1}".format(self.item_counter), level=log.INFO)

    def process_item(self, item, spider):
        if spider.name == 'ttse_equity_listing':
            return item
        if spider.name == 'ttse_bond_listing':
            return self.process_bond_item(item)
        if spider.name in ['ttse_equity_data']:
            if isinstance(item, TickerItem):
                return self.process_ticker_item(item)
            if isinstance(item, MarketSummaryItem):
                return self.process_market_summary_item(item)
            if isinstance(item, CapValueItem):
                return self.process_capvalue_item(item)
            if isinstance(item, MarketCapValueItem):
                return self.process_mkt_capvalue_item(item)
        if spider.name in ['jse_equity']:
            if isinstance(item, TickerItem):
                return self.process_ticker_item(item)
            if isinstance(item, JSEIndexItem):
                return self.process_jse_index_item(item)

    def process_jse_index_item(self, item):
        exchange = Exchange.objects.get(code=item['exchange'])
        dateix = parse(item['dateix'])
        dd = make_aware(datetime(dateix.year, dateix.month, dateix.day),
                        get_current_timezone()
                        )
        defaults = {}
        default_mapper = {
            'jse_market_index': 'main_index',
            'jse_composite_index': 'index1',
            'jse_cross_index': 'index2',
            'jse_market_index_volume': 'volume',
        }
        for k, v in default_mapper.iteritems():
            val = self.to_float(item[k])
            if val:
                defaults[v] = val
        #import ipdb; ipdb.set_trace()
        obj, created = MarketSummary.objects.get_or_create(
            dateix=dd,
            exchange=exchange,
            defaults=defaults
        )

        if created:
            log.msg(
                "Added new observation %s" % obj
            )
        else:
            for k, v in default_mapper.iteritems():
                val = self.to_float(item[k])
                #import pdb; pdb.set_trace()
                if val:
                    setattr(obj, v, val)
            obj.save()
            log.msg("Edited observation {}".format(obj))
        return item

    def process_ticker_item(self, item):
        exchange = Exchange.objects.get(code=item['exchange'])
        dateix = parse(item['dateix'])
        dd = make_aware(
            datetime(
                dateix.year,
                dateix.month,
                dateix.day),
            get_current_timezone()
        )

        if not item.get('volume'):
            return item
        if not self.to_float(item['volume']):
            return item
        log.msg(
            "Procesing Ticker %s" % item['ticker'],
            level=log.DEBUG
        )
        symbol = Symbol.objects.get(
            exchange=exchange,
            ticker=item['ticker']
        )
        defaults = {}
        default_mapper = {
            'open_price': 'open_price',
            'high_price': 'high_price',
            'low_price': 'low_price',
            'close_price': 'close_price',
            'volume': 'volume'
        }

        for k, v in default_mapper.iteritems():
            val = self.to_float(item[k])
            if val:
                defaults[v] = val
        defaults['exchange_code'] = item['exchange']

        obj, created = SymbolData.objects.get_or_create(
            dateix=dd,
            symbol=symbol,
            defaults=defaults
        )
        if created:
            log.msg(
                "Added new observation %s" % obj
            )
        else:

            for k, v in default_mapper.iteritems():
                val = self.to_float(item[k])
                #import pdb; pdb.set_trace()
                if val:
                    setattr(obj, v, val)
            obj.exchange_code = item['exchange']
            obj.save()
            log.msg("Edited observation {}".format(obj))
        return item

    def process_bond_item(self, item):

        itype = InstrumentType.objects.get(pk=1)
        defaults = {
            "symbol": item["symbol"],
            "instrument_type": itype,
            "security_name": item["security_name"],
            "short_name": item["short_name"],
            "description": item["description"]
        }
        obj, created = Security.objects.get_or_create(
            isin=item['isin'],
            defaults=defaults
        )
        op_str = "Added new Bond"
        if not created:
            op_str = "Updated Bond"
            for k, v in defaults.iteritems():
                setattr(obj, k, v)
            obj.save()
            stats.inc_value('updated_item_count')
        else:
            stats.inc_value('created_item_count')

        log.msg("%s %s" % (op_str,
                item['isin']), level=log.DEBUG
                )
        return item

    def process_market_summary_item(self, item):
        exchange = Exchange.objects.get(code=item['exchange'])
        dateix = parse(item['dateix'])
        dd = make_aware(datetime(dateix.year, dateix.month, dateix.day),
                        get_current_timezone()
                        )
        # import ipdb; ipdb.set_trace()
        log.msg("Process market summary", level=log.DEBUG)
        defaults = {}
        default_mapper = {
            'composite_ix': 'main_index',
            'alltt_ix': 'index1',
            'cross_ix': 'index2',
            'total_market_volume': 'volume',
            'total_market_value': 'value_traded'
        }
        for k, v in default_mapper.iteritems():
            val = self.to_float(item[k])
            if val:
                defaults[v] = val
        #import ipdb; ipdb.set_trace()
        obj, created = MarketSummary.objects.get_or_create(
            dateix=dd,
            exchange=exchange,
            defaults=defaults
        )
        if created:
            log.msg("Added new observation %s[%s]=[C:%s V:%s]" % (
                    item['exchange'], dateix.strftime('%Y-%m-%d'),
                    defaults['volume'],
                    defaults['main_index']), level=log.DEBUG)
        else:
            for k, v in default_mapper.iteritems():
                val = self.to_float(item[k])
                #import pdb; pdb.set_trace()
                if val:
                    setattr(obj, v, val)
            obj.save()
        return item

    def process_mkt_capvalue_item(self, item):
        exchange = Exchange.objects.get(code=item['exchange'])
        dateix = parse(item['dateix'])
        dd = make_aware(datetime(dateix.year, dateix.month, dateix.day),
                        get_current_timezone()
                        )
        # import ipdb; ipdb.set_trace()
        log.msg("Process Market Cap", level=log.DEBUG)
        defaults = {}
        default_mapper = {
            'capital_value': 'market_cap',
            'trade_count': 'trade_count',
        }
        for k, v in default_mapper.iteritems():
            val = self.to_float(item[k])
            if val:
                defaults[v] = val
        #import ipdb; ipdb.set_trace()
        obj, created = MarketSummary.objects.get_or_create(
            dateix=dd,
            exchange=exchange,
            defaults=defaults
        )
        if created:
            log.msg("Added new observation %s[%s]=[C:%s V:%s]" % (
                    item['exchange'], dateix.strftime('%Y-%m-%d'),
                    defaults['market_cap'],
                    defaults['trade_count']), level=log.DEBUG)
        else:
            for k, v in default_mapper.iteritems():
                val = self.to_float(item[k])
                #import pdb; pdb.set_trace()
                if val:
                    setattr(obj, v, val)
            obj.save()
        return item

    def process_capvalue_item(self, item):

        exchange = Exchange.objects.get(code=item['exchange'])
        dateix = parse(item['dateix'])
        dd = make_aware(
            datetime(dateix.year, dateix.month, dateix.day),
            get_current_timezone())
        log.msg("Processing CapValueItem", level=log.INFO)
        try:
            symbol = Symbol.objects.get(
                exchange=exchange,
                ticker=item['ticker']
            )
        except Symbol.DoesNotExist:
            log.msg("Symbol {0} {1} does not exist".format(
                    item['exchange'], item['ticker']), level=log.WARNING)
            return item

        # only update Market cap/value traded if there a trade for that day
        if item['traded_value']:
            try:
                obj = SymbolData.objects.get(dateix=dd,symbol=symbol)
                obj.value_traded = self.to_float(item['traded_value'])
                obj.market_cap = self.to_float(item['capital_value'])
                obj.save()
            except SymbolData.DoesNotExist:
                obj = SymbolData(dateix=dd, symbol=symbol)
                obj.value_traded = self.to_float(item['traded_value'])
                obj.market_cap = self.to_float(item['capital_value'])
                obj.save()

                log.msg("Updated {}".format(obj), level=log.INFO)

        c = symbol.company

        try:
            obj, created = ShareIssue.objects.get_or_create(
                dateix=dd,
                company=c,
                defaults={
                    'outstanding': self.to_float(item['issued_capital'])
                }
            )
        except Exception, e:
            print e

            # if not created:
            #     obj.outstanding = self.to_float(item['issued_capital'])
            #     obj.save()

        return item

