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


@app.cli.command('initdb')
def init_db():
    '''Connect to mysql.'''
    db = pymysql.connect(host=current_app.config['HOST'],
                         user=current_app.config['USERNAME'],
                         password=current_app.config['PASSWORD'],
                         db=current_app.config['DB'],
                         charset=current_app.config['CHARSET']
    )
    g['db'] = db
    print('Initialized the database.')







@app.route("/")
def index_page():
    return render_template("index.html") 

