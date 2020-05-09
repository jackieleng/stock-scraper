# -*- coding: utf-8 -*-
import re
from typing import Tuple

import scrapy
from twisted.python.failure import Failure

from ..items import StockScraperItem


PATTERN = re.compile(r"(?P<company_name>.+)\s\((?P<ticker>\^?.+)\)")


def parse_name(name_plus_ticker: str) -> Tuple[str, str]:
    """Extract company name and ticker symbol from string."""
    match = PATTERN.match(name_plus_ticker)
    if match:
        company_name = match.group('company_name')
        ticker_symbol = match.group('ticker')
        return company_name, ticker_symbol
    raise ValueError


class YahooFinanceStocksSpider(scrapy.Spider):
    name = 'yahoo_finance'
    allowed_domains = ['finance.yahoo.com']
    start_urls = [
        "https://finance.yahoo.com/quote/TSLA?p=TSLA",
        "https://finance.yahoo.com/quote/RDSA.AS?p=RDSA.AS",
        "https://finance.yahoo.com/quote/^GSPC?p=^GSPC",
        "https://finance.yahoo.com/quote/NONEXSITING?p=NONEXISTING",
        "https://finance.yahoo.com/quote/NVDA?p=NVDA",
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback)

    def parse(self, response: scrapy.http.TextResponse):
        self.log("Parse")
        self.log(response.url)
        title = response.xpath('//title/text()')[0].get()
        name = response.xpath('//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1/text()')[0].get()
        price = response.xpath('//*[@id="quote-header-info"]/div[3]/div/div/span[1]/text()')[0].get()
        ticker_from_url = response.url.split('?')[0].split('/')[-1]

        try:
            company_name, ticker_symbol = parse_name(name)
        except ValueError:
            item = StockScraperItem(name=name, price=price, ticker=ticker_from_url)
        else:
            item = StockScraperItem(name=company_name, price=price, ticker=ticker_symbol)
        yield item

    def errback(self, failure: Failure):
        self.log('Failure')
        self.log(failure)
