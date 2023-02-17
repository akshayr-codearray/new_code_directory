from bson.json_util import dumps
from flask import Flask, request, make_response, jsonify
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from celery import Celery

app = Flask(__name__)
api = Api(app)
app.config["MONGO_URI"] = "mongodb://mongo:27017/myDatabase"
mongo = PyMongo(app)

celery = Celery(app.name, broker='amqp://guest:guest@amqp:5672/', result_backend='redis://redis:6379/0')


class User(Resource):

    def get(self):
        user_list = []
        user_data = mongo.db.users
        for user in user_data.find():
            user_list.append(user)
        return dumps(user_list)

    def post(self):
        if request.is_json:
            try:
                data = request.get_json()
                name = data['name']
                email = data['email']
                user_id = data['user_id']

                mytask = post_user.delay(user_id, name, email)
                # print(mytask)
                res_of_task = mytask.get()
                # print(res_of_task)
                if res_of_task == 'user already exist':
                    return jsonify({"message": f"User Already Exist with id {user_id}"})
                else:
                    return jsonify({"message": "User Added Successfully "})

                # if user_id not in [i['user_id'] for i in mongo.db.users.find()]:
                #
                #     mongo.db.users.insert_one({"name": name, "email": email, "user_id": user_id})
                #     return make_response({"message": "user added successfully"}, 201)
                # else:
                #     return make_response({"message": f"user with id {user_id} already exist please use different id"},
                #                          400)

            except KeyError:
                return make_response({"message": "invalid json format",
                                      "valid format": {"name": "your_name",
                                                       "email": "your_email",
                                                       "user_id": "id"}}, 400)


class One_User(Resource):

    def get(self, u_id):
        try:
            if u_id in [i['user_id'] for i in mongo.db.users.find()]:
                user = mongo.db.users.find_one({"user_id": u_id})
                return dumps(user)
            else:
                return make_response({"message": "Enter valid 'user_id' "}, 400)

        except KeyError:
            return make_response({"message": "something went wrong"}, 404)

    def put(self, u_id):
        if request.is_json:
            try:
                data = request.get_json()
                email = data['email']
                name = data['name']
                mytask = put_user.delay(u_id, email, name)

                res_of_task = mytask.get()
                if res_of_task == 'updated':
                    return make_response({"message": f"User with id  {u_id} updated successfully"}, 201)
                else:
                    return make_response({"message": f"User with id  {u_id} doesn't exist"}, 400)
            # if u_id in [i['user_id'] for i in mongo.db.users.find()]:
            #
            #     myquery = {"user_id": u_id}
            #     values = {"$set": {"email": data['email'], "name": data['name']}}
            #
            #     mongo.db.users.update_one(myquery, values)
            #
            #     return make_response({"message": "user updated successfully"}, 201)
            #
            # else:
            #     return make_response({"message": f"no user exist with id {u_id}"})

            except KeyError:
                return make_response({"message": "something went wrong"}, 404)

    def delete(self, u_id):
        try:
            user_id = u_id
            # user_ids = []
            # for user in mongo.db.users.find():
            #     user_ids.append(user['user_id'])
            if user_id in [i['user_id'] for i in mongo.db.users.find()]:
                mongo.db.users.delete_one({"user_id": user_id})
                return make_response({"message": f'user with id {user_id} deleted'}, 200)
            else:
                return make_response({"message": "enter valid 'user_id'"}, 404)

        except KeyError:
            return make_response({"message": "something went wrong"}, 400)


@celery.task()
def post_user(user_id, name, email):
    with app.app_context():
        if user_id not in [i['user_id'] for i in mongo.db.users.find()]:

            mongo.db.users.insert_one({"name": name, "email": email, "user_id": user_id})
            return "User added successfully"
        else:

            return "user already exist"


@celery.task()
def put_user(u_id, email, name):
    with app.app_context():
        if u_id in [i['user_id'] for i in mongo.db.users.find()]:

            myquery = {"user_id": u_id}
            values = {"$set": {"email": email, "name": name}}

            mongo.db.users.update_one(myquery, values)
            return "updated"
        else:
            return "not updated"


api.add_resource(User, '/')
api.add_resource(One_User, '/one/<int:u_id>')

