'''API interface for papers

GET /api/papers/ : return all the papers in db.
GET /api/papers/?author_id= : return papers wroten that author.
GET /api/papers/?group_id= : return papers wroten by authors in the group.
'''

from flask import Blueprint, request, jsonify, g
from flask.views import MethodView


def select_papers_by_author(author_id):
    '''All the papers from the author, so no duplicate will be found'''

    sql = "SELECT * FROM authors_and_papers WHERE author_id=%s"
    papers = []
    with g.db.cursor() as cursor:
        cursor.execute(sql, (author_id,))
        paper_id_list = cursor.fetchall()
        sql = "SELECT * FROM papers WHERE id=%s"
        for each in paper_id_list:
            cursor.execute(sql, (each['paper_id'],))
            papers += cursor.fetchall()
    return papers


def select_papers_by_group(group_id):
    '''Since may find same papers from different authors, may find duplicate'''

    papers = []
    already_list = []
    sql1 = "SELECT * FROM authors_and_groups WHERE group_id=%s"
    sql2 = "SELECT * FROM authors_and_papers WHERE author_id=%s"
    sql3 = "SELECT * FROM papers WHERE id=%s"

    with g.db.cursor() as cursor:
        # find the author_id list
        cursor.execute(sql1, (group_id,))
        author_id_list = cursor.fetchall()
        for each in author_id_list:
            cursor.execute(sql2, (each['author_id'],))
            paper_id_list = cursor.fetchall()
            for each in paper_id_list:
                if each['paper_id'] in already_list:
                    continue
                else:
                    already_list.append(each['paper_id'])
                    cursor.execute(sql3, (each['paper_id'],))
                    papers += cursor.fetchall()
    return papers

class PaperAPI(MethodView):
    def get(self):
        author_id = request.args.get("author_id", None)
        group_id = request.args.get("group_id", None)
        if author_id:
            papers = select_papers_by_author(author_id)
        elif group_id:
            papers = select_papers_by_group(group_id)
        else:
            pass

        return jsonify(papers)


papers_blueprint = Blueprint('papers', __name__, url_prefix='/api')

paper_view = PaperAPI.as_view('papers')
papers_blueprint.add_url_rule('/papers/', view_func=paper_view, methods=['GET'])
