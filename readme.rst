=====================================
Scrapers for Caribbean Stock Markets
=====================================

This is intended to be a collection of scrapers for Caribbean Stock markets.
While many of the stock exchange websites provide a convenient CSV dump
URL unfortunately these
only provide the most basic data i.e closing prices and volumes.
We aim to provide the following data for each markets

* Market Summary

    * Main Index - Composite Index
    * Volume
    * Value Traded
    * Resident company index, Volume and Value
    * Composite

* Symbol Data

    * OHLCV
    * Market Cap
    * Value Traded

* Listed Securities

    * Equities
    * Bonds

* Ex Dividend Periods

===========
Change Log
===========

0.0.1 (2012-10-08)
==================

* Added a TTSE daily equity scraper that more or less works. Supports
  crawling over a single date ::

    scrapy crawl ttse -a start_date=2012-01-05

  Crawl over a date range ::

    scrapy crawl ttse -a start_date=2012-01-05 -a end_date=2012-03-01


  The spider provides the following data

    * Equity Market Summary

        - composite_ix
        - total_market_volume
        - total_market_value
        - total_trades
        - alltt_ix
        - tt_volume
        - tt_value
        - tt_trades
        - cross_ix
        - cross_volume
        - cross_value
        - cross_trades

     * For each Traded equity

        - open_price
        - high_price
        - low_price
        - close_price
        - volume
        - ticker
        - issued_capital
        - capital_value
        - trade_count
        - traded_value

* Date Range crawling functionality requires pandas but we plan to replace
  with ``dateutils.rrules``.

* We've done a pipeline to support Django model loading. We'd like to
  find an elegant way of decoupling scrapy from our custom
  django stuff since your model is likely to be different from mine.





