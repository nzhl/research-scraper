import scrapy
import centipede.items
import re

class GoogleSpider(scrapy.Spider):
    name = "gs.unuk.cs"

    start_urls = [
            'https://scholar.google.com/citations?mauthors=computer+science+nottingham&hl=en&view_op=search_authors'
    ]

    def parse(self, response):
        for author_url in response.css("h3.gsc_1usr_name a::attr(href)").extract():
            yield response.follow(author_url, callback=self.parse_author)

        # next page
        next_page_url = response.css("button.gs_btnPR.gs_in_ib.gs_btn_half.gs_btn_srt::attr(onclick)").extract_first()
        if next_page_url:
            next_page_url = next_page_url[17:-1].replace("\\x3d", "=").replace("\\x26", "&")
            yield response.follow(next_page_url, callback=self.parse)

    def parse_author(self, response):
        if response.url.find("cstart") == -1:
            # first page
            author = centipede.items.Author()
            author['name'] = response.css("#gsc_prf_in::text").extract_first()
            author['tags'] = ""
            for each_tag in response.css("a.gsc_prf_ila::text").extract():
                author['tags'] += each_tag + ','
            author['tags'] = author['tags'].strip(", ")
            author['url'] = response.url
            yield author

            next_page_url = response.url + "&cstart=20&pagesize=20"
        else:
            cstart = int(re.findall("cstart=(.*)&", response.url)[0]) + 20
            next_page_url = re.sub("cstart=(.*)&", "cstart=%d&" % cstart, response.url)

        for each_paper_url in response.css("a.gsc_a_at::attr(href)"):
            yield response.follow(each_paper_url, callback=self.parse_paper)
        if not len(response.css("#gsc_bpf_next.gs_dis")):
            yield scrapy.Request(next_page_url, callback=self.parse_author)

    def parse_paper(self, response):
        paper = centipede.items.Paper()
        paper['title'] = response.css("a.gsc_title_link::text").extract_first()
        if paper.get('title') == None:
            paper['title'] = response.css("#gsc_title::text").extract_first()

        selector_list = response.css("div.gs_scl")
        capture_fields = ['authors', 'publication_date', 'journal', 'conference', 'publisher', 'total_citations']
        for each_selector in selector_list:
            field = each_selector.css(".gsc_field::text").extract_first().lower().strip().replace(" ", "_")
            if field not in capture_fields:
                continue
            if field == 'total_citations':
                content = each_selector.css(".gsc_value>div>a::text").extract_first().split(" ")[-1]
                paper[field] = content
                continue
            content = each_selector.css(".gsc_value::text").extract_first().strip()
            paper[field] = content

        for field in capture_fields:
            if paper.get(field) == None:
                paper[field] = ""

        if response.css(".gsc_title_ggt::text").extract_first() == "[PDF]":
            paper['is_pdf'] = "1"
            paper['url'] = response.css("div.gsc_title_ggi>a::attr(href)").extract_first()
        else:
            paper['is_pdf'] = "0"
            paper['url'] = ""

        return paper
