from re import findall, sub
from datetime import datetime

from scrapy import Item, Field, Request, Spider
from scrapy.crawler import CrawlerProcess

from pymysql import connect
from pymysql.cursors import DictCursor


class Paper(Item):
    title = Field()
    authors = Field()
    publication_date = Field()
    conference = Field()
    journal = Field()
    publisher = Field()
    total_citations = Field()
    gs_link = Field()
    pdf_link = Field()


class DBPipeline(object):
    def open_spider(self, spider):
        self.db = connect(
                host="localhost",
                user="root",
                password="nzhl",
                db="research_scraper",
                charset='utf8mb4',
                cursorclass=DictCursor)

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):

        sql = ("INSERT INTO papers (title, authors, publication_date, conference,"
               "journal, publisher, total_citations, gs_link, pdf_link ) VALUES "
               "(%s, %s, %s, %s, %s, %s, %s, %s, %s)")

        with self.db.cursor() as cursor:
            cursor.execute(sql, (
                item['title'], item['authors'], item['publication_date'],
                item['conference'], item['journal'], item['publisher'],
                item['total_citations'], item['gs_link'], item['pdf_link']))
            print(cursor.mogrify(sql, (
                item['title'], item['authors'], item['publication_date'],
                item['conference'], item['journal'], item['publisher'],
                item['total_citations'], item['gs_link'], item['pdf_link'])))
            sql = "SELECT id FROM papers WHERE gs_link = %s"
            cursor.execute(sql, (item['gs_link'],))
            paper_id = cursor.fetchone()['id']

            sql = "INSERT INTO authors_and_papers VALUES (%s, %s)"
            cursor.execute(sql, (spider.author_id, paper_id))

        self.db.commit()
        return item


'''scrapy crawl author -a url=<author-scholar-page> -a author_id=<author_id>'''

class AuthorSpider(Spider):
    name = "author"

    def start_requests(self):
        yield Request(self.url, self.parse_author)

    def parse_author(self, response):
        if response.url.find("cstart") == -1:
            next_page_url = response.url + "&cstart=20&pagesize=20"
        else:
            cstart = int(findall("cstart=(.*)&", response.url)[0]) + 20
            next_page_url = sub("cstart=(.*)&", "cstart=%d&" % cstart, response.url)


        for each_paper_url in response.css("a.gsc_a_at::attr(href)"):
            yield response.follow(each_paper_url, callback=self.parse_paper)
        if not len(response.css("#gsc_bpf_next.gs_dis")):
            yield Request(next_page_url, callback=self.parse_author)

    def parse_paper(self, response):
        paper = Paper()
        paper['title'] = response.css("a.gsc_title_link::text").extract_first()
        if not paper.get('title'):
            paper['title'] = response.css("#gsc_title::text").extract_first()

        selector_list = response.css("div.gs_scl")
        capture_fields = [
                'authors', 'publication_date',
                'journal', 'conference',
                'publisher', 'total_citations']

        for each_selector in selector_list:
            field = (each_selector.css(".gsc_field::text")
                    .extract_first().lower().strip().replace(" ", "_"))
            if field not in capture_fields:
                #ignore unnecessary field
                pass
            elif field == 'total_citations':
                content = (each_selector.css(".gsc_value>div>a::text")
                        .extract_first().split(" ")[-1])
                paper[field] = content
                continue
            else:
                content = each_selector.css(".gsc_value::text").extract_first().strip()
                paper[field] = content

        for field in capture_fields:
            if paper.get(field) == None:
                paper[field] = ""
        if not paper['total_citations']:
            paper['total_citations'] = "0";
            
        paper['gs_link'] = response.urljoin(response.url)
        if response.css(".gsc_title_ggt::text").extract_first() == "[PDF]":
            paper['pdf_link'] = (response.css("div.gsc_title_ggi>a::attr(href)")
                    .extract_first())
        else:
            paper['pdf_link'] = ""

        if paper['publication_date'].count("/") != 2:
            # complete the date
            if not paper['publication_date']:
                paper['publication_date'] = None
            elif paper['publication_date'].count("/") == 1:
                paper['publication_date'] = (datetime.strptime(
                    paper['publication_date'], "%Y/%m").date().strftime("%Y/%m/%d"))
            else:
                paper['publication_date'] = (datetime.strptime(
                    paper['publication_date'], "%Y").date().strftime("%Y/%m/%d"))
        return paper

def strat_crawler(url, author_id):
    process = CrawlerProcess({ 
        'DOWNLOAD_DELAY':2,
        'USER-AGENT':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) '
                     'Presto/2.8.131 Version/11.11',
        #'LOG_FILE':
        #'LOG_STDOUT':False
        'ITEM_PIPELINES':{'AuthorSpider.DBPipeline':300,}
    })
    process.crawl(AuthorSpider, url=url, author_id=author_id)
    process.start()

strat_crawler('https://scholar.google.com/citations?user=gWbK0A0AAAAJ&hl=en', 2)
