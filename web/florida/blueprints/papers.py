'''This is the blueprint file that defined user api interface.

GET http://host_name/api/papers?author_id=...
    - no body required
'''

from flask import Blueprint, request, jsonify, g, current_app, abort
from flask.views import MethodView


def select_papers_by_author(author_id):
    '''Search papers by author id.'''

    sql = "SELECT * FROM authors_and_papers WHERE author_id=%s"
    papers = []
    with g.db.cursor() as cursor:
        cursor.execute(sql, (author_id,))
        result = cursor.fetchall()
        sql = "SELECT * FROM papers WHERE id=%s"
        for entry in result:
            cursor.execute(sql, (entry['paper_id'],))
            papers += cursor.fetchall()
    return papers


def select_papers_by_group(group_id):
    '''Search papers by group id.'''

    papers = []
    already_list = []
    sql = "SELECT * FROM authors_and_groups WHERE group_id=%s"
    with g.db.cursor() as cursor:
        cursor.execute(sql, (group_id,))
        result = cursor.fetchall()
        sql1 = "SELECT * FROM authors_and_papers WHERE author_id=%s"
        for entry in result:
            cursor.execute(sql1, (entry['author_id'],))
            result = cursor.fetchall()
            sql2 = "SELECT * FROM papers WHERE id=%s"
            for entry in result:
                if entry['paper_id'] in already_list:
                    continue
                else:
                    already_list.append(entry['paper_id'])

                cursor.execute(sql2, (entry['paper_id'],))
                papers += cursor.fetchall()

    return papers

def insert_paper(paper):
    '''Insert a new paper into database.

    Necessary field : 'authors', 'title'
    '''

    necessary_fields = ['authors', 'title']
    for field in necessary_fields:
        if field not in paper or paper[field] == "":
            abort(400)
    option_fields = ['conference', 'journal', 'publication_date',
              'publisher', 'total_citations', 'is_pdf', 'url']
    for field in option_fields:
        if not paper.get(field):
            paper[field] = ""

    sql = "INSERT INTO articles VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)"
    affected_rows = 0
    if not hasattr(g, 'db'):
        connect_db()
    with g.db.cursor() as cursor:
        #print(cursor.mogrify(sql), ...)
        affected_rows = cursor.execute(sql, (
            paper['title'], paper['authors'],
            paper['publication_date'], paper['conference'],
            paper['journal'], paper['publisher'],
            paper['total_citations'], paper['is_pdf'],
            paper['url']))
        g.db.commit()
        return affected_rows

def update_paper(paper_id, paper):
    '''Using delete then insert to have a ugly implementation'''

    delete_paper(paper_id)
    insert_paper(paper)


def delete_paper(paper_id):
    sql = "DELETE FROM articles WHERE id=%s"
    affected_rows = 0
    if not hasattr(g, 'db'):
        connect_db()
        with g.db.cursor() as cursor:
            affected_rows = cursor.execute(sql, (paper_id,))

    g.db.commit()
    return affected_rows


class PaperAPI(MethodView):
    def get(self):
        papers = []
        author_id = request.args.get("author_id", None)
        group_id = request.args.get("group_id", None)
        if author_id:
            papers = select_papers_by_author(author_id)
        elif group_id:
            papers = select_papers_by_group(group_id)
        return jsonify(papers)

    def post(self):
        author_id = request.args.get("author_id", None)
        if author_id:



            def put(self, paper_id):
                paper = request.get_json()
        update_paper(paper_id, paper)
        return ("", 200, {})


    def delete(self, paper_id):
        if delete_paper(paper_id) == 0:
            abort(404)
            return ("", 200, {})


papers_blueprint = Blueprint('papers', __name__, url_prefix='/api')

paper_view = PaperAPI.as_view('papers')
papers_blueprint.add_url_rule('/papers/', view_func=paper_view, methods=['GET'])
