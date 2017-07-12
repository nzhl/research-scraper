'''This is the blueprint file that defined user api interface.

GET http://host_name/api/papers?query=...
    - no body required

POST http://host_name/api/papers/
    - with a json-formatted body which contains the necessary fields of articles.

PUT http://host_name/api/papers/paper_id
    - with a json-formatted body which contains the ncessary fields of articles.

DELETE http://host_name/api/papers/paper_id
    - no body required
'''

from flask import Blueprint, request, jsonify, g, current_app, abort
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

def select_paper(field, query):
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

def insert_paper(paper):
    '''Insert a new paper into database.

    Necessary field : 'authors', 'title'
    '''

    necessary_fields = ['authors', 'title']
    for field in necessary_fields:
        if field not in paper or paper[field] == "":
            abort(400)
    option_fields = ['conference', 'journal', 'publication_date',
              'publisher', 'total_citations', 'is_pdf', 'url']
    for field in option_fields:
        if not paper.get(field):
            paper[field] = ""

    sql = "INSERT INTO articles VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)"
    affected_rows = 0
    if not hasattr(g, 'db'):
        connect_db()
    with g.db.cursor() as cursor:
        #print(cursor.mogrify(sql), ...)
        affected_rows = cursor.execute(sql, (
            paper['title'], paper['authors'],
            paper['publication_date'], paper['conference'],
            paper['journal'], paper['publisher'],
            paper['total_citations'], paper['is_pdf'],
            paper['url']))
        g.db.commit()
        return affected_rows

def update_paper(paper_id, paper):
    '''Using delete then insert to have a ugly implementation'''

    delete_paper(paper_id)
    insert_paper(paper)


def delete_paper(paper_id):
    sql = "DELETE FROM articles WHERE id=%s"
    affected_rows = 0
    if not hasattr(g, 'db'):
        connect_db()
        with g.db.cursor() as cursor:
            affected_rows = cursor.execute(sql, (paper_id,))

    g.db.commit()
    return affected_rows


class PaperAPI(MethodView):
    def get(self):
        papers = []
        query = request.args.get('query')
        if query:
            search_fields = ["authors", "title"]
            for field in search_fields:
                papers += select_paper(field, query)
                return jsonify({'count': len(papers), 'papers': papers })

    def post(self):
        paper = request.get_json()
        if insert_paper(paper) == 0:
            abort(409)
            return ("", 201, {})


    def put(self, paper_id):
        paper = request.get_json()
        update_paper(paper_id, paper)
        return ("", 200, {})


    def delete(self, paper_id):
        if delete_paper(paper_id) == 0:
            abort(404)
            return ("", 200, {})


api_bp = Blueprint('api', __name__, url_prefix='/api')

paper_api_view = PaperAPI.as_view('papers')
api_bp.add_url_rule('/papers/', view_func=paper_api_view, methods=['GET', 'POST'])
api_bp.add_url_rule('/papers/<int:paper_id>', view_func=paper_api_view, methods=['PUT', 'DELETE'])

