import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


## ROUTES
@app.route('/drinks')
def get_drinks():
    '''
    Get all drinks in short format representation from the Database.
    
    :returns: status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.all()
    drinks_formatted = [drink.short() for drink in drinks]
    
    return jsonify({
        'success': True,
        'drinks': drinks_formatted
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    '''
    Get all drinks in long format representation from the Database.
    
    :returns: status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure.
    '''
    drinks = Drink.query.all()
    drinks_formatted = [drink.long() for drink in drinks]
    
    return jsonify({
        'success': True,
        'drinks': drinks_formatted
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    '''
    Create a new drink in the drinks table.
    
    :returns: status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    '''
    data = request.get_json()

    try:
        title = data['title']
        recipe = data['recipe']
    except KeyError:
        abort(400)

    if not title or not recipe:
        abort(400)
    
    new_drink = Drink(title=title, recipe=recipe)

    try:
        new_drink.insert()
    except:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    '''
    Updates the drink if it exists, otherwise returns a 404 error.
    
    :param drink_id: Existing drink model id.
    :returns: status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
    '''
    drink = Drink.query.get(drink_id)
    
    if not drink:
        abort(404)
        
    data = request.get_json()
    
    try:
        title = data['title']
        recipe = data['recipe']
    except KeyError:
        abort(400)
        
    try:
        drink.title = title
        drink.recipe = recipe
        
        drink.update()
    except:
        abort(400)
        
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    '''
    Deletes the drink if it exists, otherwise returns a 404 error.
    
    :param drink_id: Existing drink model id.
    :returns: status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
    '''
    drink = Drink.query.get(drink_id)
    
    if not drink:
        abort(404)
    
    drink.delete()
    
    return jsonify({
        'success': True,
        'delete': drink_id
    })


## Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': "Unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': "Forbidden"
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "Resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': "Unprocessable"
    }), 422


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': "Internal error"
    }), 500
