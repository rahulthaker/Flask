from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required,
                                get_jwt_claims,
                                jwt_optional,
                                get_jwt_identity,
                                fresh_jwt_required)
from models.item import ItemModel


class Items(Resource):
    @jwt_optional
    def get(self):
        user_id=get_jwt_identity()
        items=[item.json() for item in ItemModel.find_all()]
        if user_id:
            return {'items':items},200

        else:
            return {
                'items':[item['name'] for item in items],
                'message':'More information available if logged in'
            },200

        return {'items':[item.json() for item in ItemModel.find_all()]}  #list(map(lambda x:x.json() ,ItemModel.query.all()

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field cannot be left blank')
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help='Every item needs a store id')


    @jwt_required
    def get(self,name):
        item=ItemModel.find_by_name(name)
        if item:
            return item.json()
        else: #can be removed will work implicitly
            return {'message':'item not found'} ,404


    @fresh_jwt_required
    def post(self,name):
        if ItemModel.find_by_name(name):
            return {'message':'Item with the given name already exists'},400

        data= Item.parser.parse_args()  #force=True to ignore errors and header or silent=True to return None
        item=ItemModel(name,data['price'],data['store_id'])

        try:
            item.save_to_db()
        except:
            return {'message':'An error occurred while inserting the item'}, 500 #Internal server eror


        return item.json(), 201


    @jwt_required
    def delete(self,name):
        claims=get_jwt_claims()
        if not claims['is_admin']:
            return {'message':'Requires admin previlege'},401
        item=ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        else:
            return {"message":'Item does not exist'}
        return {"message":"item deleted"}

    def put(self,name):
        data=Item.parser.parse_args()
        item= ItemModel.find_by_name(name)
        if item is None:
            item=ItemModel(name,data['price'],data['store_id'])
        else:
            item.price=data['price']
            item.store_id=data['store_id']

        item.save_to_db()
        return item.json()
