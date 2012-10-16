# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy import log
from markets.models import Symbol, Exchange, SymbolData, MarketSummary,\
    ShareIssue
from trading.models import Security, InstrumentType
from carib_stockex_scrapers.items import BondListingItems, MarketSummaryItem, \
    TickerItem, CapValueItem
from dateutil.parser import parse
from django.utils.timezone import get_current_timezone, make_aware
from datetime import datetime


class DjangoLoaderPipeline(object):
    def to_float(self, instr):
        try:
            return(float(instr))
        except (ValueError, TypeError, AttributeError):
            return None

    def process_item(self, item, spider):
        if isinstance(item, BondListingItems):
            log.msg("Processing Bond Listing %s" % item, level=log.DEBUG)
            itype = InstrumentType.objects.get(
                description="Debt Instrument")
            defaults = {
                "symbol": item["symbol"],
                "security_type": itype,
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
            #import ipdb; ipdb.set_trace()
            log.msg("%s %s" % (op_str,
                    item['isin']), level=log.DEBUG
                    )
            return item
        if isinstance(item, MarketSummaryItem):
            exchange = Exchange.objects.get(code=item['exchange'])
            dateix = parse(item['dateix'])
            dd = make_aware(datetime(dateix.year, dateix.month, dateix.day),
                            get_current_timezone()
                            )
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
        if isinstance(item, CapValueItem):
            exchange = Exchange.objects.get(code=item['exchange'])
            dateix = parse(item['dateix'])
            dd = make_aware(datetime(dateix.year, dateix.month, dateix.day),
                            get_current_timezone())
            log.msg("Processing CapValueItem", level=log.DEBUG)
            symbol = Symbol.objects.get(
                exchange=exchange,
                ticker=item['ticker']
            )
            #update Market cap Value Traded
            defaults = {
                'value_traded': self.to_float(item['traded_value']),
                'market_cap': self.to_float(item['capital_value']),
            }

            obj, created = SymbolData.objects.get_or_create(
                dateix=dd,
                symbol=symbol,
                defaults=defaults
            )
            if not created:
                for k, v in defaults.iteritems():
                    setattr(obj, k, self.to_float(v))
                obj.save()

            log.msg("Updated %s[%s]=Val[%s] K[%s]" % (
                    item['ticker'],
                    dd.strftime('%Y-%m-%d'),
                    self.to_float(item['traded_value']),
                    self.to_float(item['capital_value'])
                    )
                    )
            issued_capital = self.to_float(item['issued_capital'])
            if not issued_capital:
                return item
            # try:
            #     sh = symbol.company.shareissue_set.get()
            #     # sh.dateix = dateix
            #     # sh.outstanding = issued_capital
            #     # sh.save()
            # except ShareIssue.DoesNotExist:
            #     sh = ShareIssue(
            #         company=symbol.company,
            #         dateix=dateix,
            #         outstanding=issued_capital
            #     )
            #     import ipdb; ipdb.set_trace()
            #     sh.save()
            # log.msg("Upadated share issue for %s[%s]=%s" %
            #         (symbol, dateix, issued_capital)
            # )
            return item
        if isinstance(item, TickerItem):

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
                obj.save()
                log.msg("Edited observation %s" % obj
                )
            return item
