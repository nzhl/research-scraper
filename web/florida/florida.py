from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app
import pymysql 

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY='development key',
    HOST='localhost',
    USERNAME='root',
    PASSWORD='nzhl',
    DB='unnc_scholar',
    CHARSET='utf8mb4'
))


@app.teardown_appcontext
def close_db(error):
    '''Close mysql connection'''
    if hasattr(g, 'db'):
        g.db.close()
        print("close db")

@app.route("/", methods=['get'])
def index_page():
    articles = []
    query = request.args.get('query')
    if query:
        search_fields = ["authors", "title"]
        for field in search_fields:
            articles += select_field(field, query)

    return render_template("index.html", articles=articles) 

def get_db():
    '''Get connection to mysql.'''

    db = pymysql.connect(host=current_app.config['HOST'],
                         user=current_app.config['USERNAME'],
                         password=current_app.config['PASSWORD'],
                         db=current_app.config['DB'],
                         charset=current_app.config['CHARSET'],
                         cursorclass=pymysql.cursors.DictCursor
    )
    g.db = db
    return db

def select_field(field, query):
    sql = 'SELECT * FROM articles WHERE %s LIKE "%%%s%%";' % (field, query)
    result = []
    if not hasattr(g, 'db'):
        get_db()
    with g.db.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    return result
