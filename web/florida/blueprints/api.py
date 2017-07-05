'''This is the blueprint file that defined restful api interface.

GET http://host_name/api/papers?query=...
    - no body required

POST http://host_name/api/papers/
    - with a json formatted body which contains all the fields of articles.

PUT http://host_name/api/papers/paper_id
    - with a json formatted body which contains some/all the fields of articles.

DELETE http://host_name/api/papers/paper_id
    - no body required

'''

from flask import Blueprint, request, jsonify, g, current_app
from flask.views import MethodView
import pymysql

def connect_db():
    '''Get connection to mysql.'''

    db = pymysql.connect(host=current_app.config['HOST'],
            user=current_app.config['USERNAME'],
            password=current_app.config['PASSWORD'],
            db=current_app.config['DB'],
            charset=current_app.config['CHARSET'],
            cursorclass=pymysql.cursors.DictCursor)
    g.db = db
    return db

def select_field(field, query):
    '''Search all the entry of which field contains the query.'''

    #field won't passed by client, so need not to be defensive
    sql = "SELECT * FROM articles WHERE " + field + " LIKE %s" 
    result = []
    if not hasattr(g, 'db'):
        connect_db()
    with g.db.cursor() as cursor:
        cursor.execute(sql, ('%'+query+'%',))
        #print(cursor._last_executed)

        result = cursor.fetchall()
    return result

class PaperAPI(MethodView):
    def get(self):
        papers = []
        query = request.args.get('query')
        if query:
            search_fields = ["authors", "title"]
            for field in search_fields:
                papers += select_field(field, query)
        return jsonify({'count': len(papers), 'papers': papers })

    def post(self):
        return 'post'


    def put(self, paper_id):
        return 'put'


    def delete(self, paper_id):
        return 'delete'

api_bp = Blueprint('api', __name__, url_prefix='/api')

paper_api_view = PaperAPI.as_view('papers')
api_bp.add_url_rule('/papers/', view_func=paper_api_view,
                     methods=['GET', 'POST'])
api_bp.add_url_rule('/papers/<int:paper_id>', view_func=paper_api_view,
                     methods=['PUT', 'DELETE'])
