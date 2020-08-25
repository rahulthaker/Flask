from db import db
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
api=Api(app)

app.config['JWT_AUTH_URL_RULE']='/login'  #do this before creating the JWT instance or it wont affect
app.config['JWT_EXPIRATION_DELTA']=timedelta(seconds=1800)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'  #can use other databases as well
#app.config['JWT_AUTH_USERNAME_KEY']='email'

@app.before_first_request
def create_tables():
    db.create_all()


jwt=JWT(app, authenticate ,identity)


api.add_resource(Item,'/item/<string:name>')
api.add_resource(Items,'/item')
api.add_resource(UserRegister,'/register')
api.add_resource(Store,'/Store/<string:name>')
api.add_resource(StoreList,'/Store')

if __name__=='__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)