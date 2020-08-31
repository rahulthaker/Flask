import os
from flask import Flask,jsonify
from flask_restful import Api
from resources.user import UserRegister,User,UserLogin,TokenRefresher,UserLogout
from resources.item import Items,Item
from datetime import timedelta
from resources.store import Store,StoreList
from flask_jwt_extended import JWTManager
from db import db
from blacklist import BLACKLIST

app=Flask(__name__)
app.secret_key='Rahul' #app.config['JWT_SECRET_KEY']='Rahul'

app.config['DEBUG'] = True
#app.config['JWT_AUTH_URL_RULE']='/login'  #do this before creating the JWT instance or it wont affect
app.config['JWT_EXPIRATION_DELTA']=timedelta(seconds=1800)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL','sqlite:///data.db')  #can use other databases as well
app.config['PROPAGATE_EXCEPTIONS']=True
app.config['JWT_BLACKLIST_ENABLED']=True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
#app.config['JWT_AUTH_USERNAME_KEY']='email'

api=Api(app)

jwt=JWTManager(app)


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:   # instead of hard-coding, we should read from a config file to get a list of admins instead
        return {'is_admin': True}
    return {'is_admin': False}

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):  # we have to keep the argument here, since it's passed in by the caller internally
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401


api.add_resource(Item,'/item/<string:name>')
api.add_resource(Items,'/item')
api.add_resource(UserRegister,'/register')
api.add_resource(Store,'/Store/<string:name>')
api.add_resource(StoreList,'/Store')
api.add_resource(User,'/user/<int:user_id>')
api.add_resource(UserLogin,'/login')
api.add_resource(TokenRefresher,'/refresh')
api.add_resource(UserLogout,'/logout')

db.init_app(app)

if __name__=='__main__':
    if app.config['DEBUG']:
        @app.before_first_request
        def create_tables():
            db.create_all()
    app.run(port=5000, debug=True)