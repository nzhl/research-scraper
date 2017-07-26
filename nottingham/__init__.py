from flask import Flask, g, render_template, current_app, session
from flask.json import JSONEncoder
from .blueprints.sessions import sessions_blueprint
from .blueprints.authors import authors_blueprint
from .blueprints.papers import papers_blueprint
from .blueprints.groups import groups_blueprint
from datetime import date
import pymysql

# jsonify response converts datetime object into string with GMT
# https://stackoverflow.com/questions/43663552/keep-a-datetime-date-in-yyyy-mm-dd-format-when-using-flasks-jsonify
class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app = Flask(__name__)

app.json_encoder = CustomJSONEncoder

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
app.register_blueprint(groups_blueprint)


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

@app.route("/edit_groups/", methods=['GET'])
def edit_groups_page():
    return render_template('edit_groups.html')

@app.route("/authors/<int:author_id>")
def authors_page(author_id):
    return render_template('authors.html', author_id=author_id)

@app.route("/groups/<int:group_id>")
def groups_page(group_id):
    return render_template('groups.html', group_id=group_id)
