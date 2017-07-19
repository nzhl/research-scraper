import scrapy
import re
import datetime

from crawler.items import Paper

'''scrapy crawl author -a url=<author-scholar-page> author_id=<author_id>'''

class AuthorSpider(scrapy.Spider):
    name = "author"

    def start_requests(self):
        url = getattr(self, 'url', None)
        author_id = getattr(self, 'author_id', None)
        if url and author_id:
            self.author_id = author_id
            yield scrapy.Request(url, self.parse_author)
        else:
            print("Parameter Url Required !")

    def parse_author(self, response):
        if response.url.find("cstart") == -1:
            next_page_url = response.url + "&cstart=20&pagesize=20"
        else:
            cstart = int(re.findall("cstart=(.*)&", response.url)[0]) + 20
            next_page_url = re.sub("cstart=(.*)&", "cstart=%d&" % cstart, response.url)


        for each_paper_url in response.css("a.gsc_a_at::attr(href)"):
            yield response.follow(each_paper_url, callback=self.parse_paper)
        if not len(response.css("#gsc_bpf_next.gs_dis")):
            yield scrapy.Request(next_page_url, callback=self.parse_author)

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
                paper['publication_date'] = (datetime.datetime
                        .strptime(paper['publication_date'], "%Y/%m")
                        .date().strftime("%Y/%m/%d"))
            else:
                paper['publication_date'] = (datetime.datetime
                        .strptime(paper['publication_date'], "%Y")
                        .date().strftime("%Y/%m/%d"))

        return paper
