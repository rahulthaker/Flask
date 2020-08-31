from blacklist import BLACKLIST
from flask_restful import Resource,reqparse
from models.User import UserModel
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                jwt_required,
                                get_raw_jwt)

class UserRegister(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument("username",
                        type=str,
                        required=True,
                        help='This field cannot be empty',
                        )
    parser.add_argument("password",
                        type=str,
                        required=True,
                        help='This field cannot be empty',
                        )
    def post(self):
        data= UserRegister.parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return {'message':'username already exists'},400

        user=UserModel(**data)
        user.save_to_db()

        return {'message':'User created successfully '} , 201

class User(Resource):
    @classmethod
    def get(self,user_id):
        user=UserModel.find_by_id(user_id)
        if not user:
            return {'message':'User not found'},404
        else:
            return user.json()


    @classmethod
    def delete(cls,user_id):
        user=UserModel.find_by_id(user_id)
        if not user:
            return {"message":"User does not exit"},404

        else:
            return user.delete_from_db()

class UserLogin(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument("username",
                        type=str,
                        required=True,
                        help='This field cannot be empty',
                        )
    parser.add_argument("password",
                        type=str,
                        required=True,
                        help='This field cannot be empty',
                        )

    @classmethod
    def post(cls):
        data=cls.parser.parse_args()
        user=UserModel.find_by_username(data['username'])

        if user and user.password==data['password']:
            access_token=create_access_token(identity=user.id,fresh=True)
            refresh_token=create_refresh_token(user.id)
            return{
                      'access_token':access_token,
                      'refresh_token':refresh_token
                  },200

        return {'message':'Invalid credential'},401


class TokenRefresher(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user=get_jwt_identity()
        new_token=create_access_token(identity=current_user,fresh=False)
        return {'access_token':new_token},200


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti=get_raw_jwt()['jti']  #JTI is a unique Id an identifier for JWT
        BLACKLIST.add(jti)
        return {'message':'Successfully logged out'},200

