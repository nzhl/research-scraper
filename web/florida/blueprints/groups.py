'''This is the blueprint file that defined user api interface.

GET http://host_name/api/papers?author_id=...
    - no body required
'''

from flask import Blueprint, request, jsonify, g, session
from flask.views import MethodView


def select_groups_by_author(author_id):
    '''Search groups by author id.'''

    sql = "SELECT * FROM authors_and_groups WHERE author_id=%s"
    groups = []
    with g.db.cursor() as cursor:
        cursor.execute(sql, (author_id,))
        result = cursor.fetchall()
        sql = "SELECT * FROM groups WHERE id=%s"
        for entry in result:
            cursor.execute(sql, (entry['group_id'],))
            groups += cursor.fetchall()
    return groups


def select_groups_by_keyword(keyword):
    sql = "SELECT * FROM groups WHERE name LIKE %s"
    groups = []
    with g.db.cursor() as cursor:
        cursor.execute(sql, ('%' + keyword + '%',))
        groups = cursor.fetchall()
    return groups


def insert_group(group):
    '''Insert a new group into database.'''

    sql = "INSERT INTO groups (name, description) VALUES (%s, %s)"
    affected_rows = 0
    with g.db.cursor() as cursor:
        #print(cursor.mogrify(sql), ...)
        affected_rows = cursor.execute(sql, (group['name'], group['description']))
        if not affected_rows:
            return 0
        sql = "SELECT id FROM groups WHERE name=%s AND description=%s"
        affected_rows = cursor.execute(sql, (group['name'], group['description']))
        result = cursor.fetchall()
        sql = "INSERT INTO authors_and_groups VALUES (%s, %s)"
        for each in group['selected']:
            affected_rows = cursor.execute(sql, (each, result[0]['id']))
            if not affected_rows:
                return 0
        g.db.commit()
    return affected_rows


class GroupView(MethodView):
    
    def get(self):
        groups = []
        keyword = request.args.get("keyword", None)
        author_id = request.args.get("author_id", None)

        if author_id:
            groups = select_groups_by_author(author_id)
        elif keyword:
            groups = select_groups_by_keyword(keyword)

        return jsonify(groups)

    def post(self):
        group = request.get_json()
        if not insert_group(group):
            return ("", 409, {})
        return ("", 200, {})


groups_blueprint = Blueprint('groups', __name__, url_prefix='/api')

groups_view = GroupView.as_view('groups')
groups_blueprint.add_url_rule('/groups/', view_func=groups_view, methods=['GET', 'POST'])

