from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()

        if not json.get('username'):
            return {'error': 'Username required'}, 422
        if not json.get('image_url'):
            return {'error': 'Image URL required'}, 422
        if not json.get('bio'):
            return {'error': 'Bio required'}, 422
        
        user = User(
            username = json['username'],
            image_url=json['image_url'],
            bio=json['bio']
        )

        user.password_hash = json['password']

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return user.to_dict(), 201


class CheckSession(Resource):
    def get(self):
        user = User.query.filter(
            User.id == session.get('user_id')).first()
        if user:
            return user.to_dict(), 200
        else:
            return {
                'message': 'Unauthorized'
            }, 401


class Login(Resource):
    def post(self):
        user = User.query.filter(
            User.username == request.get_json()['username']).first()
        if user:
            session['user_id'] = user.id
            return user.to_dict()
        else:
            return {'message': 'Invalid Login Credentials'}, 401


class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return {}, 204
        else:
            return {'error': 'Unauthorized'}, 401


class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()

        if session['user_id']:
            recipes_dict = [recipe.to_dict() for recipe in user.recipes]
            return recipes_dict, 200
        else:
            return {'error': 'Unauthorized'}, 401
        
    def post(self):
        user = User.query.filter(User.id == session.get('user_id')).first()

        if not user:
            return {'error': 'Unauthorized'}, 401
        
        json = request.get_json()

        if not json.get('title'):
            return {'error': 'Title is required.'}, 422
        if not json.get('instructions'):
            return {'error': 'Instructions are required.'}, 422
        if len(json.get('instructions')) < 50:
            return {'error': 'Instructions must be at least 50 characters long.'}, 422
        if not json.get('minutes_to_complete'):
            return {'error': 'Minutes to complete are required.'}, 422
        if not isinstance(json.get('minutes_to_complete'), int) or json['minutes_to_complete'] <= 0:
            return {'error': 'Minutes to complete must be a positive integer.'}, 422
        
        new_recipe = Recipe(
            title = json['title'],
            instructions = json['instructions'],
            minutes_to_complete=json['minutes_to_complete'],
            user_id = user.id
        )
        db.session.add(new_recipe)
        db.session.commit()

        return new_recipe.to_dict(), 201


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)


if __name__ == '__main__':
    app.run(port=5555, debug=True)