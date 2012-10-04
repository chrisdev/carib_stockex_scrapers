# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy import log
from markets.models import Symbol,Exchange,SymbolData,MarketSummary
from django.utils.timezone import utc,get_current_timezone,get_default_timezone,make_aware
from datetime import datetime
class DjangoLoaderPipeline(object):
    def to_float(self,instr):
        try:
            return(float(instr))
        except (ValueError,TypeError,AttributeError):
            return None

    def process_item(self, item, spider):
        exchange=Exchange.objects.get(code=item['exchange'])
        dateix=item['dateix']
        dd=make_aware(datetime(dateix.year,dateix.month,dateix.day),
                                      get_current_timezone())
        if 'composite_ix' in item.fields:
            log.msg("Process market summary",level=log.DEBUG)
            defaults={}
            default_mapper={
                'composite_ix':'main_index',
                'alltt_ix':'index1',
                'cross_ix':'index2',
                 'total_market_volume':'volume',
                 'total_market_value':'value_traded'
                }
            for k,v in default_mapper.iteritems():
               val = self.to_float(item[k])
               if val:
                   defaults[v]=val
            import ipdb; ipdb.set_trace()
            obj,created = MarketSummary.objects.get_or_create(dateix=dd,
                            exchange=exchange,
                            defaults=defaults)
            if created:
                log.msg("Added new observation %s[%s]=[C:%s V:%s]" % (
                        item['exchange'],dateix.strftime('%Y-%m-%d'),
                        defaults['volume'],
                        defaults['main_index']),level=log.DEBUG)                
            else:
                for k,v in default_mapper.iteritems():
                   val = self.to_float(item[k])
                   #import pdb; pdb.set_trace()
                   if val:
                       setattr(obj,v,val)
                obj.save()

        else:
            log.msg("Procesing Ticker %s" % item['ticker'],level=log.DEBUG)
            symbol=Symbol.objects.get(exchange=exchange,ticker=item['ticker'])
            defaults={}
            default_mapper = {
                'open_price':'open_price',
                'high_price':'high_price',
                'low_price':'low_price',
                'close_price':'close_price',
                'volume':'volume'
             }

            for k,v in default_mapper.iteritems():
               val = self.to_float(item[k])
               if val:
                   defaults[v]=val
            defaults['exchange_code']='TTSE'

            obj,created = SymbolData.objects.get_or_create(dateix=dd,
                          symbol=symbol,
                          defaults=defaults)
            if created:
                log.msg("Added new observation %s[%s]=[C:%s V:%s]" % (symbol.ticker,
                                                dd.strftime('%Y-%m-%d'),
                                                defaults['close_price'],
                                                defaults['volume'])
                       )


            else:
                log.msg("Edited observation %s[%s]" % (symbol.ticker,
                                                dd.strftime('%Y-%m-%d'))
                        )

                for k,v in default_mapper.iteritems():
                   val = self.to_float(item[k])
                   #import pdb; pdb.set_trace()
                   if val:
                       setattr(obj,v,val)
                obj.save()

        return item
