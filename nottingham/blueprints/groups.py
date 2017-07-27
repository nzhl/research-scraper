
from flask import Blueprint, request, jsonify, g, session
from flask.views import MethodView

def select_all_groups():
    sql = "SELECT * FROM groups"
    with g.db.cursor() as cursor:
        cursor.execute(sql)
        groups = cursor.fetchall()
    return groups


def select_group_by_id(group_id):
    sql = "SELECT * FROM groups WHERE id = %s"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (group_id,))
        group = cursor.fetchone()
    return group


def select_groups_by_author(author_id):
    sql = "SELECT * FROM authors_and_groups WHERE author_id=%s"
    groups = []
    with g.db.cursor() as cursor:
        cursor.execute(sql, (author_id,))
        result = cursor.fetchall()
        sql = "SELECT * FROM groups WHERE id=%s"
        for entry in result:
            cursor.execute(sql, (entry['group_id'],))
            group = cursor.fetchone()
            group['is_manager'] = entry['is_manager']
            group['before_date'] = entry['before_date']
            group['after_date'] = entry['after_date']
            groups.append(group)
    return groups


def insert_group(group):
    sql = ("INSERT INTO groups (name, description, group_link) VALUES "
          "(%s, %s, %s)")
    with g.db.cursor() as cursor:
        #print(cursor.mogrify(sql), ...)
        cursor.execute(sql, (group['name'],
             group['description'], group['group_link'],))
        sql = "SELECT id FROM groups WHERE name=%s AND description=%s"
        cursor.execute(sql, (group['name'], group['description']))
        group_id = cursor.fetchone()['id']
        sql = ("INSERT INTO authors_and_groups (author_id, group_id) "
              "VALUES (%s, %s)")
        for author_id in group['selected']:
            cursor.execute(sql, (author_id, group_id))
        sql = ("UPDATE authors_and_groups SET is_manager=1 WHERE "
               "author_id=%s AND group_id=%s")
        cursor.execute(sql, (session['id'], group_id))
    g.db.commit()


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

def update_filter(group):
    sql = ("UPDATE authors_and_groups SET before_date=%s, after_date=%s WHERE "
           "author_id=%s and group_id=%s")

    with g.db.cursor() as cursor:
        cursor.execute(sql, (group['before_date'], group['after_date'],
                             session['id'], group['group_id']))
    g.db.commit()

def delete_group(group_id):
    sql = "DELETE FROM groups WHERE id=%s"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (group_id,))
        sql = "DELETE FROM authors_and_groups WHERE group_id=%s"
        cursor.execute(sql, (group_id,))
        sql = "DELETE FROM hide_authors_and_groups WHERE group_id=%s"
        cursor.execute(sql, (group_id,))
        sql = "DELETE FROM show_authors_and_groups WHERE group_id=%s"
        cursor.execute(sql, (group_id,))
    g.db.commit()

def insert_hide(data):
    sql = "INSERT INTO hide_papers_and_groups VALUES (%s, %s)"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (data['paper_id'], data['group_id']),)
    g.db.commit()

def insert_show(data):
    sql = "INSERT INTO show_papers_and_groups VALUES (%s, %s)"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (data['paper_id'], data['group_id']),)
    g.db.commit()

def delete_hide(data):
    sql = ("DELETE FROM hide_papers_and_groups WHERE paper_id=%s "
           "AND group_id=%s")
    with g.db.cursor() as cursor:
        re = cursor.execute(sql, (data['paper_id'], data['group_id']),)
    g.db.commit()
    return re


def delete_show(data):
    sql = ("DELETE FROM show_papers_and_groups WHERE paper_id=%s "
           "AND group_id=%s")
    with g.db.cursor() as cursor:
        re = cursor.execute(sql, (data['paper_id'], data['group_id']),)
    g.db.commit()
    return re


class GroupView(MethodView):
    
    def get(self, group_id = None):
        if group_id != None:
            groups = select_group_by_id(group_id)
            return jsonify(groups)

        author_id = request.args.get("author_id", None)
        if author_id:
            groups = select_groups_by_author(author_id)
        else:
            groups = select_all_groups()
        return jsonify(groups)

    def post(self):
        group = request.get_json()
        # login check then insert
        if 'id' not in session:
            return ("", 409, {})
        insert_group(group)
        return ("", 200, {})

    def put(self, group_id):
        data = request.get_json()
        data['group_id'] = group_id
        if 'id' not in session:
            return ("", 404, {})
        if data['type'] == "group":
            update_group(data)
        elif data['type'] == "filter":
            update_filter(data)
        elif data['type'] == "hide":
            if not delete_show(data):
                insert_hide(data)
        elif data['type'] == "show":
            if not delete_hide(data):
                insert_show(data)
        return ("", 200, {})

    def delete(self, group_id):
        if 'id' not in session:
            return ("", 404, {})
        delete_group(group_id)
        return ("", 200, {})





groups_blueprint = Blueprint('groups', __name__, url_prefix='/api')
groups_view = GroupView.as_view('groups')

groups_blueprint.add_url_rule('/groups/<int:group_id>',
        view_func=groups_view,
        methods=['GET', 'PUT', 'DELETE'])

groups_blueprint.add_url_rule('/groups/',
        view_func=groups_view,
        methods=['GET', 'POST'])

