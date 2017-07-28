import os
import csv

from flask import request, jsonify, send_from_directory
from flask.views import MethodView

from dsert import assert_valid_dict


def register_draft_routes(blueprint):
    draft_view_func = DraftRoutes.as_view('draft')
    blueprint.add_url_rule('/draft/<string:draft_id>/player/result', strict_slashes=False, view_func=draft_view_func, methods=['POST'])
    # blueprint.add_url_rule('/draft/<string:draft_id>/result', strict_slashes=False, view_func=draft_view_func, methods=['GET'])

class DraftRoutes(MethodView):

    def get(self, draft_id):
        # csv reader setup
        print("huh")
        return jsonify("working"), 200
        # return send_from_directory('drafts', "%s.csv" % draft_id, as_attachment=True)


    def post(self, draft_id):
        body = request.get_json()
        # paxos what upppp
        assert_valid_dict(body, known_types={'name': unicode, 'amount': int, 'owner': unicode})

        # csv writer setup
        myfile = open('drafts/%s.csv' % draft_id, 'a')
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)

        csv_row = [body["name"], body["owner"], body["amount"]]

        try:
            wr.writerow(csv_row)
        except UnicodeEncodeError:
            return jsonify(error="error writing file"), 500

        return jsonify(result="success"), 201
