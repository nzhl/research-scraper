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

    papers = []

    sql = ("SELECT d.* from (SELECT paper_id, before_date, after_date FROM "
           "authors_and_papers AS a INNER JOIN authors_and_groups AS b ON "
           "a.author_id=b.author_id WHERE group_id=%s) AS c INNER JOIN "
           "papers AS d ON paper_id=id AND publication_date >= after_date "
           "AND publication_date <= before_date")

    with g.db.cursor() as cursor:
        cursor.execute(sql, (group_id,))
        papers = cursor.fetchall()
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
