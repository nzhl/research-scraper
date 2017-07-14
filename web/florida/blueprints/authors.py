'''This is the blueprint file that defined restful api interface for author data.

GET http://host_name/api/authors/?keyword=
    - search authors which contain the keyword
    - return a json list.

POST http://host_name/api/authors/
    - registration
    - 203 : register successfully
    - 409 : conflict data or illegal parameter
'''

from flask import Blueprint, request, jsonify, g, abort, session
from flask.views import MethodView
from . import sessions


def select_authors_like(keyword):
    sql = "SELECT name, id FROM authors WHERE name LIKE %s"

    result = []
    with g.db.cursor() as cursor:
        cursor.execute(sql, ('%' + keyword + '%',))
        result = cursor.fetchall()

    return result

def select_authors():
    sql = "SELECT name, id FROM authors"
    result = []
    with g.db.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    return result


def insert_authors(author):
    '''Insert a new author data into database'''

    sql = "INSERT INTO authors (name, is_registered, account, password, gs_link) VALUES (%s, %s, %s, %s, %s)"

    affected_rows = 0
    with g.db.cursor() as cursor:
        affected_rows = cursor.execute(sql, (
            author['name'], author['is_registered'],
            author['account'], author['password'],
            author['gs_link'],))
        #print(cursor._last_executed)

    g.db.commit()
    return affected_rows


class AuthorView(MethodView):

    def get(self):
        '''search'''

        authors = []
        keyword = request.args.get('keyword', None)

        if keyword:
            authors = select_authors_like(keyword)
        elif len(list(request.args.keys())) == 0:
            authors = select_authors()

        return jsonify(authors)

    def post(self):
        '''Login'''

        author = request.get_json()
        if not insert_authors(author):
            return ("", 409)
        else:
            author = sessions.select_authors(author['account'], author['password'])[0]
            session['id'] = author['id']
            session['name'] = author['name']
            return ("", 201)


authors_blueprint = Blueprint('authors', __name__, url_prefix='/api')
authors_view = AuthorView.as_view('authors')
authors_blueprint.add_url_rule('/authors/', view_func=authors_view, methods=['GET'])
authors_blueprint.add_url_rule('/authors/', view_func=authors_view, methods=['POST'])
