from flask.views import MethodView


class GitDocumentApi(MethodView):
    def post(self):
        return {"msg": "success"}, 201

    def patch(self):
        return {"msg": "success"}, 201
