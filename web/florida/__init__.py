from flask import Flask, g, render_template, request
from florida.blueprints.api import api_bp

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY='development key',
    HOST='localhost',
    USERNAME='root',
    PASSWORD='nzhl',
    DB='unnc_scholar',
    CHARSET='utf8mb4'
))

app.register_blueprint(api_bp)

@app.teardown_appcontext
def close_db(error):
    '''Close mysql connection'''
    if hasattr(g, 'db'):
        g.db.close()

