'''This is the blueprint file that defined restful api interface for author data.

GET /api/authors/id= : return the specific author
GET /api/authors/ : return all
GET /api/authors/?group_id= : return authors inside the group


POST http://host_name/api/authors/
    - registration
    - 203 : register successfully
    - 409 : conflict data or illegal parameter
'''


from flask import Blueprint, request, jsonify, g, abort, session
from flask.views import MethodView
from . import sessions

import subprocess

def select_author_by_id(author_id):
    '''Find the author with the specific id

    But only id, name, gs_link will be returned since 
    this is a public interface.
    '''

    sql = "SELECT id,name,gs_link FROM authors WHERE id=%s"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (author_id,))
        author = cursor.fetchone()
    return author


def select_all_authors():
    sql = "SELECT id, name, gs_link FROM authors"
    with g.db.cursor() as cursor:
        cursor.execute(sql)
        authors = cursor.fetchall()
    return authors


def select_authors_by_group(group_id):
    sql = "SELECT * FROM authors_and_groups WHERE group_id=%s"
    authors = []
    with g.db.cursor() as cursor:
        cursor.execute(sql, (group_id,))
        result = cursor.fetchall()
        sql = "SELECT name, id, gs_link FROM authors WHERE id=%s"
        for each in result:
            cursor.execute(sql, (each['author_id'],))
            authors += cursor.fetchall()
    return authors

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

    def get(self, author_id = None):
        if author_id != None:
            author = select_author_by_id(author_id)
            return jsonify(author)

        group_id = request.args.get('group_id', None)
        if group_id:
            authors = select_authors_by_group(group_id)
        else:
            authors = select_all_authors()
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
            subprocess.Popen([
                "python", "/root/work/Research-Scraper/src/init.py",
                author['gs_link'], str(author['id'])])
            return ("", 201)


authors_blueprint = Blueprint('authors', __name__, url_prefix='/api')
authors_view = AuthorView.as_view('authors')

authors_blueprint.add_url_rule('/authors/<int:author_id>',
        view_func=authors_view,
        methods=['GET'])

authors_blueprint.add_url_rule('/authors/',
        view_func=authors_view,
        methods=['GET', 'POST'])
