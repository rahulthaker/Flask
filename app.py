import os
from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
from security import authenticate,identity
from resources.user import UserRegister
from resources.item import Items,Item
from datetime import timedelta
from resources.store import Store,StoreList

app=Flask(__name__)
app.secret_key='Rahul'

app.config['DEBUG'] = True
app.config['JWT_AUTH_URL_RULE']='/login'  #do this before creating the JWT instance or it wont affect
app.config['JWT_EXPIRATION_DELTA']=timedelta(seconds=1800)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL','sqlite:///data.db')  #can use other databases as well
#app.config['JWT_AUTH_USERNAME_KEY']='email'

api=Api(app)

jwt=JWT(app, authenticate ,identity)


api.add_resource(Item,'/item/<string:name>')
api.add_resource(Items,'/item')
api.add_resource(UserRegister,'/register')
api.add_resource(Store,'/Store/<string:name>')
api.add_resource(StoreList,'/Store')

if __name__=='__main__':
    from db import db
    if app.config['DEBUG']:
        @app.before_first_request
        def create_tables():
            db.create_all()
    app.run(port=5000, debug=True)