'''The file defines the author api


This api will only return authors' id, name and gs_link
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- GET /api/authors/id 
    return the specific author
- GET /api/authors/ 
    return all
- GET /api/authors/?group_id= 
    return authors inside the group
- POST /api/authors/ 
    - registration
         request body with the json
    - 203 
         register successfully
    - 409 
         conflict data or illegal parameter
'''

from subprocess import Popen

from flask import (Blueprint, request, jsonify, g, abort,
                   session, redirect, url_for)
from flask.views import MethodView
from .sessions import select_authors, SessionView


ALLOWED_FIELDS = "id, name, gs_link"

def select_author_by_id(author_id):
    sql = "SELECT " + ALLOWED_FIELDS + " FROM authors WHERE id=%s"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (author_id,))
        author = cursor.fetchone()
    return author

def select_all_authors():
    sql = "SELECT " + ALLOWED_FIELDS + " FROM authors WHERE is_registered=True"
    with g.db.cursor() as cursor:
        cursor.execute(sql)
        authors = cursor.fetchall()
    return authors

def select_authors_by_group(group_id):
    sql = ("SELECT " + ALLOWED_FIELDS + " FROM authors_and_groups "
           "INNER JOIN authors ON author_id=id WHERE group_id=%s AND is_registered=True")
    with g.db.cursor() as cursor:
        #print(cursor.mogrify(sql, (group_id,)))
        cursor.execute(sql, (group_id,))
        authors = cursor.fetchall()
    return authors

def insert_author(author):
    sql = ("INSERT INTO authors (name, account, password, "
           "gs_link) VALUES (%s, %s, %s, %s)")

    with g.db.cursor() as cursor:
        cursor.execute(sql, (author['name'], author['account'],
                             author['password'], author['gs_link'],)
        )
        sql = "SELECT * FROM authors WHERE account=%s AND password=%s"
        cursor.execute(sql, (author['account'], author['password']))
        author = cursor.fetchone()
    g.db.commit()
    return author

def insert_author_with_code(author):
    sql = ("UPDATE authors SET name=%s, account=%s, password=%s, gs_link=%s, "
           "is_registered=1 WHERE id=%s")
    with g.db.cursor() as cursor:
        cursor.execute(sql, (author['name'], author['account'],
                             author['password'], author['gs_link'],
                             author['invitation_code'],))
        sql = "SELECT * FROM authors WHERE account=%s AND password=%s"
        cursor.execute(sql, (author['account'], author['password']))
        author = cursor.fetchone()
    g.db.commit()
    return author

def insert_raw_author():
    sql = "INSERT INTO authors (is_registered) VALUES (0)"
    with g.db.cursor() as cursor:
        cursor.execute(sql)
        g.db.commit()
        sql = "SELECT LAST_INSERT_ID()"
        cursor.execute(sql)
        return cursor.fetchone()['LAST_INSERT_ID()']
    
def update_gs_link(data):
    sql = "UPDATE authors SET gs_link=%s WHERE id=%s"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (data['gs_link'], data['id']))
        sql = "DELETE FROM authors_and_papers WHERE author_id=%s"
        cursor.execute(sql, (data['id'],))
    g.db.commit()


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
        author = request.get_json()
    
        if author['invitation_code']:
            author = insert_author_with_code(author)
        else:
            author = insert_author(author)

        Popen(["python", "web/spiders/AuthorSpider.py",
               author['gs_link'], str(author['id']) ]
        )
        
        # redirect with HTTP method preserved 
        # https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask
        return redirect('api/sessions/', code=307)

    def put(self):
        data = request.get_json()
        if 'id' not in session:
            return ("", 404, {})
        data['id'] = session['id']
        if data['type'] == "gs_link":
            update_gs_link(data)
            Popen(["python", "web/spiders/AuthorSpider.py",
                   data['gs_link'], str(data['id']) ]
            )
        else:
            pass
        return ("", 200, {})


authors_blueprint = Blueprint('authors', __name__, url_prefix='/api')
authors_view = AuthorView.as_view('authors')

authors_blueprint.add_url_rule('/authors/<int:author_id>',
        view_func=authors_view,
        methods=['GET'])
authors_blueprint.add_url_rule('/authors/',
        view_func=authors_view,
        methods=['GET', 'POST', 'PUT'])
