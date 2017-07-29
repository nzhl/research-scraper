'''The module contians all the logic of the applications.

This file mainly focus on:
    1. Init the app object and set up configurations.
    2. Bind the blueprints to the app. 
    3. Register different path to different handler.
'''

from flask import Flask, g, render_template, current_app, session
from flask.json import JSONEncoder
from .blueprints.sessions import sessions_blueprint
from .blueprints.authors import authors_blueprint
from .blueprints.papers import papers_blueprint
from .blueprints.groups import groups_blueprint
from datetime import date
import pymysql


class CustomJSONEncoder(JSONEncoder):
    '''Customer defined Json encoder

    Override the default json converting rule.
    '''

    def default(self, obj):
        '''It will be used when we want to convert an object to json format.

        The flask default one will caused unwanted result, Check more `details 
        <https://stackoverflow.com/questions/43663552/keep-a-datetime-date-in-yyyy-mm-dd-format-when-using-flasks-jsonify>`_.
        
        '''

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

# those blueprints deal with 4 different api interface.
app.register_blueprint(sessions_blueprint)
app.register_blueprint(authors_blueprint)
app.register_blueprint(papers_blueprint)
app.register_blueprint(groups_blueprint)


@app.before_request
def connect_db():
    '''This function will be called right before a request come.
    
    So it's a good idea to get connection to database here.
    '''

    db = pymysql.connect(host=current_app.config['HOST'],
            user=current_app.config['USERNAME'],
            password=current_app.config['PASSWORD'],
            db=current_app.config['DB'],
            charset=current_app.config['CHARSET'],
            cursorclass=pymysql.cursors.DictCursor)
    g.db = db

@app.teardown_appcontext
def close_db(error):
    '''This function will be called before current request context over.

    We use it to close db.
    '''

    if hasattr(g, 'db'):
        g.db.close()

@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def index_page():
    '''Bind the index page'''

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
