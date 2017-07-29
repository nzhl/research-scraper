'''API interface for papers

GET /api/papers/ : return all the papers in db.
GET /api/papers/?author_id= : return papers wroten that author.
GET /api/papers/?group_id= : return papers wroten by authors in the group.
'''

from flask import Blueprint, request, jsonify, g, session
from flask.views import MethodView

def select_all_papers():
    pass


def select_papers_by_author(author_id):
    papers = []
    sql = ("SELECT papers.* FROM papers INNER JOIN authors_and_papers ON "
           "id = paper_id WHERE author_id=%s")
    with g.db.cursor() as cursor:
        cursor.execute(sql, (author_id,))
        papers = cursor.fetchall()
    return papers


def select_papers_by_group(group_id, show_hidden):
    papers = []
    if not show_hidden:
        sql = ("SELECT d.* from (SELECT paper_id, before_date, after_date FROM "
               "authors_and_papers AS a INNER JOIN authors_and_groups AS b ON "
               "a.author_id=b.author_id WHERE group_id=%s) AS c INNER JOIN "
               "papers AS d ON paper_id=id AND publication_date >= after_date "
               "AND publication_date <= before_date")
        with g.db.cursor() as cursor:
            cursor.execute(sql, (group_id,))
            papers = cursor.fetchall()
            if not papers:
                papers = []
            sql = ("SELECT * FROM papers WHERE id IN (SELECT paper_id FROM "
                  "show_papers_and_groups WHERE group_id=%s)")
            cursor.execute(sql, (group_id,))
            papers += cursor.fetchall()
            sql = "SELECT paper_id FROM hide_papers_and_groups WHERE group_id=%s"
            cursor.execute(sql, (group_id,))
            ids = []
            for each in cursor.fetchall():
                ids.append(each['paper_id'])
            re = []
            idx = 0
            for paper in papers:
                idx += 1
                if paper['id'] in ids:
                    pass
                else:
                    re.append(paper)
    else:
        sql = ("SELECT d.* from (SELECT paper_id, before_date, after_date FROM "
               "authors_and_papers AS a INNER JOIN authors_and_groups AS b ON "
               "a.author_id=b.author_id WHERE group_id=%s) AS c INNER JOIN "
               "papers AS d ON paper_id=id AND (publication_date < after_date "
               "OR publication_date > before_date)")
        with g.db.cursor() as cursor:
            cursor.execute(sql, (group_id,))
            papers = cursor.fetchall()
            if not papers:
                papers = []
            sql = ("SELECT * FROM papers WHERE id IN (SELECT "
                   "paper_id FROM hide_papers_and_groups WHERE group_id=%s)")
            cursor.execute(sql, (group_id,))
            papers += cursor.fetchall()
            sql = "SELECT paper_id FROM show_papers_and_groups WHERE group_id=%s"
            cursor.execute(sql, (group_id,))
            ids = []
            for each in cursor.fetchall():
                ids.append(each['paper_id'])
            re = []
            for paper in papers:
                if paper['id'] in ids:
                    pass
                else:
                    re.append(paper)
    return re

def tag_is_owned(papers):
    if 'id' not in session:
        return
    ids = []
    sql = "SELECT paper_id FROM authors_and_papers WHERE author_id=%s"

    with g.db.cursor() as cursor:
        cursor.execute(sql, (session['id'],))
        result = cursor.fetchall()
        for each in result:
            ids.append(each['paper_id'])
        for paper in papers:
            if paper['id'] in ids:
                paper['is_owned'] = True
            else:
                paper['is_owned'] = False


class PaperAPI(MethodView):
    def get(self):
        author_id = request.args.get("author_id", None)
        group_id = request.args.get("group_id", None)
        show_hidden = request.args.get("show_hidden", False)
        
        if author_id:
            papers = select_papers_by_author(author_id)
        elif group_id:
            papers = select_papers_by_group(group_id, show_hidden)
        else:
            papers = select_all_papers()

        tag_is_owned(papers)
        return jsonify(papers)


papers_blueprint = Blueprint('papers', __name__, url_prefix='/api')
paper_view = PaperAPI.as_view('papers')
papers_blueprint.add_url_rule('/papers/', view_func=paper_view, methods=['GET'])
