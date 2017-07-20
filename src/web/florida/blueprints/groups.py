'''This is the blueprint file that defined user api interface.

GET http://host_name/api/papers?author_id=...
    - no body required
'''

from flask import Blueprint, request, jsonify, g, session
from flask.views import MethodView

def select_group_by_id(group_id):
    sql = "SELECT * FROM groups WHERE id = %s"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (group_id,))
        group = cursor.fetchone()
    return group


def select_all_groups():
    sql = "SELECT * FROM groups"
    with g.db.cursor() as cursor:
        cursor.execute(sql)
        groups = cursor.fetchall()
    return groups


def select_groups_by_author(author_id):
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


def insert_group(group):
    '''Insert a new group into database.'''

    sql = "INSERT INTO groups (name, description, group_link) VALUES (%s, %s, %s)"
    affected_rows = 0
    with g.db.cursor() as cursor:
        #print(cursor.mogrify(sql), ...)
        affected_rows = cursor.execute(sql,
            (group['name'],
             group['description'],
             group['group_link']))
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


def update_group(group):
    sql = "UPDATE groups SET name=%s, description=%s, group_link=%s WHERE id=%s"
    with g.db.cursor() as cursor:
        affected_rows = cursor.execute(sql,
            (group['name'],
            group['description'],
            group['group_link'],
            group['group_id'],
            ))
        sql = "DELETE FROM authors_and_groups WHERE group_id=%s"
        cursor.execute(sql, (group['group_id']))
        sql = "INSERT INTO authors_and_groups VALUES (%s, %s)"
        for each in group['selected']:
            affected_rows = cursor.execute(sql, (each, group['group_id']))
    g.db.commit()
    return affected_rows



class GroupView(MethodView):
    
    def get(self, group_id = None):
        if group_id != None:
            group = select_group_by_id(group_id)
            return jsonify(group)

        author_id = request.args.get("author_id", None)
        if author_id:
            groups = select_groups_by_author(author_id)
        else:
            groups = select_all_groups()

        return jsonify(groups)

    def post(self):
        group = request.get_json()

        # login check then insert
        if 'id' not in session or not insert_group(group):
            return ("", 409, {})
        return ("", 200, {})

    def put(self, group_id):
        group = request.get_json()
        group['group_id'] = group_id
        # todo safety check
        if 'id' not in session or not update_group(group):
            return ("", 404, {})
        return ("", 200, {})




groups_blueprint = Blueprint('groups', __name__, url_prefix='/api')
groups_view = GroupView.as_view('groups')

groups_blueprint.add_url_rule('/groups/<int:group_id>',
        view_func=groups_view,
        methods=['GET', 'PUT'])

groups_blueprint.add_url_rule('/groups/',
        view_func=groups_view,
        methods=['GET', 'POST'])

