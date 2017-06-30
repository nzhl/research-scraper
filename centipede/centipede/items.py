# -*- coding: utf-8 -*-

import scrapy

class Author(scrapy.Item):
    name = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()

class Paper(scrapy.Item):
    title = scrapy.Field()
    authors = scrapy.Field()

    # following field may miss
    publication_date = scrapy.Field()
    conference = scrapy.Field()
    journal = scrapy.Field() 
    publisher = scrapy.Field() 
    total_citations = scrapy.Field()
    is_pdf = scrapy.Field()
    url = scrapy.Field()
