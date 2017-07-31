'''Manage Login / Logout API


POST http://host_name/api/sessions/
    - login, an account and password pair with json format
    - 201 : login successfully
    - 409 : error account or password

DELETE http://host_name/api/sessions/
    - logout, no parameter is needed.
    - 200 : loout successfully
'''

from flask import Blueprint, request, g, session
from flask.views import MethodView


def select_authors(account, password):
    '''Check if the corresponding authors and password pair exists'''

    sql = "SELECT * FROM authors WHERE account=%s AND password=%s"
    result = []
    with g.db.cursor() as cursor:
        cursor.execute(sql, (account, password))
        #print(cursor._last_executed)

        result = cursor.fetchall()
    return result



class SessionView(MethodView):

    def post(self):
        '''Login'''

        login_pair = request.get_json()
        result = select_authors(login_pair['account'], login_pair['password'])
        if not len(result):
            return ("", 409)
        else:
            author = result[0]
            session['id'] = author['id']
            session['name'] = author['name']
            return ("", 201, {})


    def delete(self):
        '''Logout'''

        session.clear()
        return ("", 200, {})


sessions_blueprint = Blueprint('sessions', __name__, url_prefix='/api')
sessions_view = SessionView.as_view('sessions')
sessions_blueprint.add_url_rule('/sessions/',
                                view_func=sessions_view,
                                methods=['POST', 'PUT'])
