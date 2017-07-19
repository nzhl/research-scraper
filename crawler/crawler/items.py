
import scrapy


class Paper(scrapy.Item):
    title = scrapy.Field()
    authors = scrapy.Field()

    publication_date = scrapy.Field()
    conference = scrapy.Field()
    journal = scrapy.Field() 
    publisher = scrapy.Field() 
    total_citations = scrapy.Field()
    gs_link = scrapy.Field()
    pdf_link = scrapy.Field()
