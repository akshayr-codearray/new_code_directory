from bson.json_util import dumps
from flask import Flask, request, make_response, jsonify
from flask_pymongo import PyMongo
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
app.config["MONGO_URI"] = "mongodb://mongodb-service:27017/my_DB"
mongo = PyMongo(app)


class User(Resource):

    def get(self):
        user_list = []
        user_data = mongo.db.users
        for user in user_data.find():
            user_dict = {"id":user['user_id'], "name":user['name'], "email":user['email']}
            user_list.append(user_dict)
        return make_response(jsonify(user_list))

    def post(self):
        if request.is_json:
            try:
                data = request.get_json()
                name = data['name']
                email = data['email']
                user_id = data['user_id']

                if user_id not in [i['user_id'] for i in mongo.db.users.find()]:
                    mongo.db.users.insert_one({"name": name, "email": email, "user_id": user_id})
                    return make_response({"message": "user added successfully"}, 201)
                else:
                    return make_response({"message":f"user with id {user_id} already exist please use another id"},400)

                
            except KeyError:
                return make_response({"message": "invalid json format",
                                      "valid format": {"name": "your_name",
                                                       "email": "your_email",
                                                       "user_id": "id"}}, 400)


    def put(self):
        if request.is_json:
            try:
                data = request.get_json()
                if data['user_id'] not in [i['user_id'] for i in mongo.db.users.find()]:
                    return make_response(jsonify({"message":"please enter valid 'user_id'"}))
                else:
                    myquery = {"user_id": data['user_id']}
                    values = {"$set": {"email": data['email'], "name": data['name']}}

                    mongo.db.users.update_one(myquery, values)

                    return make_response({"message": "user updated successfully"}, 201)

            except KeyError:
                return make_response({"message": "invalid json format", "valid_format": {"user_id": "id",
                                                                                         "name": "your_name",
                                                                                         "email": "your_email"
                                                                                         }}, 400)


class One_User(Resource):

    def get(self,id):
            try:
                if id in [i['user_id'] for i in mongo.db.users.find()]:
                    user = mongo.db.users.find_one({"user_id": id})
                    one_user = [{"id":user['user_id'], "name":user['name'], "email":user['email']}]
                    return make_response(jsonify(one_user))
                else:
                    return make_response({"message": f"user with id {id} do not exist"}, 404)

            except KeyError:
                return make_response({"message": "something went"}, 400)

    

    def delete(self,id):
            try:
                if id in [i['user_id'] for i in mongo.db.users.find()]:
                    mongo.db.users.delete_one({"user_id": id})
                    return make_response({"message": f'user with id {id} deleted !!!'}, 200)
                else:
                    return make_response({"message": f"user with id {id} do not exist"}, 404)

            except KeyError:
                return make_response({"message": "something went wrong"}, 400)


class Default(Resource):
    def get(self):
        return jsonify({"message":"Default endpoint modified_10"})


api.add_resource(User, '/api/user')
api.add_resource(One_User, '/api/one/<int:id>')
api.add_resource(Default,'/')
