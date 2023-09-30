from flask import Flask, jsonify, request, session
from flask_cors import CORS
import pandas
import datetime 
import json 

import pymongo 
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)

client = pymongo.MongoClient('localhost', 27017)
db = client['TreeMap']
index_collection = db["TreeDataIndex"]
data_collection = db['TreeData']
users_collection = db['Users']

def is_valid_data_id(s):
    if s == '':
        return False
    
    if not (s[0].isalnum() and s[-1].isalnum()):
        return False
    
    for char in s:
        if not (char.isalnum() or (char  in ['-', '_'])):
            return False
    
    return True


@app.route('/data/json/<name>', methods=['GET'])
def generate_json(name):

    c = data_collection.find_one( { 'name': name } )
    return jsonify(c['data'])

@app.route('/data/index', methods=['GET'])
def get_index():
    """
    Get all the Index entres from the database and sends them to the clinet.

    Returns:
        json: the json containing the list of entries.
    """
    lst = []
    for document in index_collection.find():
        lst.append({'name' : document['name'], 'display_name' : document['display_name'], 'description' : document['description']})
    return jsonify(lst)

@app.route('/data/index', methods=['PUT'])
def update_index():
    try:
        name = request.json['name']
        display_name = request.json['display_name']
        description = request.json['description']
    except:
        return jsonify({"success": False})
    
    if index_collection.count_documents({'name' : name}, limit = 1) > 0:
        #update
        index_collection.update_one({'name' : name}, {"$set": {'name' : name, 'display_name' : display_name, 'description' : description}})
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
    
@app.route('/data/index', methods=['POST'])
def add_index():
    try:
        name = str(request.json['name'])
        display_name = request.json['display_name']
        description = request.json['description']
        if len(display_name) == 0:
            return jsonify({"success": False, "message": "Display name should contain at least one character"})
        if not is_valid_data_id(name):
            return jsonify({"success": False, "message": " Must contain only chars 0-9, a-z, A-z, '_', '-'"})
    except:
        return jsonify({"success": False, "message": " Something went wrong"})
    
    if index_collection.count_documents({'name' : name}, limit = 1) > 0:
        #update
        return jsonify({"success": False, "message": " Already exists"})
    else:
        index_collection.insert_one({'name' : name, 'display_name' : display_name, 'description' : description})
        data_collection.insert_one({'name': name, 'data': []})
        return jsonify({"success": True, "message": "Index added"})
        
    
@app.route('/data/json/<name>', methods=['PUT'])
def update_json(name):
    
    data = json.loads(str(request.json['data']))
    
    if data_collection.count_documents({'name' : name}, limit = 1) == 1:
        data_collection.update_one({'name' : name}, {"$set": {'name' : name, 'data' : data}})
        return jsonify({"success": True})

    return jsonify({"success": False})
    #c = data_collection.find_one( { 'name': name } )
    #return jsonify(c['data'])


@app.route('/data/delete/<name>', methods=['DELETE'])
def delete_entry(name):
    index_collection.delete_many({'name': name})
    data_collection.delete_many({'name': name})

    return "", 204
    
## Users 

@app.route('/users/delete/<key>', methods=['DELETE'])
def delete_user(key):
    if 'log_in' in session and session['log_in'] and session['root']:
        print(key, users_collection.count_documents({'key' : key}, limit = 1))
        if users_collection.count_documents({'key' : key}, limit = 1) > 0:
            users_collection.delete_many({'key': key})
            return 'Done', 204
        else:
            return 'Not found', 404
    else:
        if 'log_in' in session and session['log_in'] and not session['root']:
            return "Don't have permission", 400
        else:
            return "Login required", 400

@app.route('/users/list', methods=['GET'])
def get_users():
    lst = []
    if 'log_in' in session and session['log_in'] and session['root']:
        for document in users_collection.find():
            lst.append({'key': document['key'],  'name': document['name'],  'root': document['root'],  'edit': document['edit'],
                        'creation_date': document['creation_date'],  'last_access': document['last_access']})
        return jsonify(lst)
    else:
        if 'log_in' in session and session['log_in'] and not session['root']:
            return "Don't have permission", 400
        else:
            return "Login required", 400

@app.route('/users/add', methods=['PUT'])
def add_user():
    if 'log_in' in session and session['log_in'] and session['root']:
        try:
            key = str(request.json['key'])
            name = str(request.json['name'])
            root = bool(request.json['root'])
            edit = bool(request.json['edit'])
            if len(key) < 6 or not key.isalnum():
                return jsonify({"success": False, "message": "key must contain at least 6 characters (a-z, A-Z, 0-9)"})
            if len(name) < 3 :
                return jsonify({"success": False, "message": "name 3 characters"})
            if root:
                edit = True
        except:
            return jsonify({"success": False, "message": "Invalid form data"})
        
        if users_collection.count_documents({'key' : key}, limit = 1) > 0:
            #update
            users_collection.update_one({'key' : key}, {"$set": {'key' : key, 'name' : name, 'root' : root, 'edit': edit, 'date_created': str(datetime.datetime.now), 'last_accessed': 'never' }})
            return jsonify({"success": True, "message": "User updated"})
        else:
            users_collection.insert_one({'key' : key, 'name' : name, 'root' : root, 'edit': edit,
                        'creation_date': str(datetime.datetime.now()),  'last_access': 'never'})
            return jsonify({"success": True, "message": "User created"})
    else:
        if 'log_in' in session and session['log_in'] and not session['root']:
            return "Don't have permission", 400
        else:
            return "Login required", 400

@app.route('/users/login', methods=['POST'])
def login():
    try:
        key = str(request.json['key'])
    
        if 'log_in' in session and session['log_in']:
            session['log_in'] = False
        if users_collection.count_documents({'key' : key}, limit = 1) > 0:
            session['log_in'] = True
            document = next(users_collection.find({'key' : key}))
            try:
                session['root'] = document['root']
                session['edit'] = document['edit']
                session['name'] = document['name']
                session['log_in'] = True
                return jsonify({"success": True, "message": "",  "root": document['root'], "edit": document['edit']})
            except:
                return jsonify({"success": False, "message": "Error occured", "root": False, "edit": False})
        else:
            return jsonify({"success": False, "message": "Invalid key", "root": False, "edit": False})
    except:
        return "Format error", 400

@app.route('/users/check_login', methods=['GET'])
def check_login():
    if users_collection.count_documents({'key' : key}, limit = 1) > 0:
        return jsonify({"success": True, "message": ""})
    else:
        return jsonify({"success": False, "message": "No user login"})

@app.route('/users/logout', methods=['GET'])
def logout():
    if 'log_in' in session and session['log_in'] == True:
        session['log_in'] = False
        print('LOGOUT')
        return "", 204
    else:
        return "", 404

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)
