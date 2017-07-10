import pymysql

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        db = pymysql.connect(host="localhost", user="root", password="nzhl", db="unnc_scholar", charset='utf8mb4')
        cursor = db.cursor()

        if isinstance(item, centipede.items.Author):
            sql = 'INSERT INTO authors VALUES ("'+ item['name'] +'", "'+ item['tags'] +'", "'+ item['url'] +'");'
        else:
            sql = 'INSERT INTO papers VALUES ("'+ item['title'] +'", "'+ item['authors'] +'", "'+ item['publication_date'] +'", "'+ item['conference'] +'", "' + item['journal'] +'", "' + item['publisher'] +'", "'+ item['total_citations'] +'", "'+ item['is_pdf'] +'", "'+ item['url'] +'");'

        try:
            cursor.execute(sql)
            db.commit()
        except:
            print(sql)
            print("DB error!")
            db.rollback()
        db.close()
