import pymysql

class DBPipeline(object):
    def open_spider(self, spider):
        self.db = pymysql.connect(
                host="localhost",
                user="root",
                password="nzhl",
                db="research_scraper",
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)

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
