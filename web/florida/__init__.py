from flask import Flask, g, render_template, current_app, session
from florida.blueprints.sessions import sessions_blueprint
from florida.blueprints.authors import authors_blueprint
from florida.blueprints.papers import papers_blueprint
import pymysql

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY='development key',
    HOST='localhost',
    USERNAME='root',
    PASSWORD='nzhl',
    DB='research_scraper',
    CHARSET='utf8mb4'
))

app.register_blueprint(sessions_blueprint)
app.register_blueprint(authors_blueprint)
app.register_blueprint(papers_blueprint)


@app.before_request
def connect_db():
    '''Get connection to mysql.'''
    db = pymysql.connect(host=current_app.config['HOST'],
            user=current_app.config['USERNAME'],
            password=current_app.config['PASSWORD'],
            db=current_app.config['DB'],
            charset=current_app.config['CHARSET'],
            cursorclass=pymysql.cursors.DictCursor)
    g.db = db

@app.teardown_appcontext
def close_db(error):
    '''Close mysql connection'''

    if hasattr(g, 'db'):
        g.db.close()

@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def index_page():
    return render_template('index.html')

@app.route("/papers/")
def author_page():
    return render_template('papers.html')

