from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas
import datetime 

import pymongo 
app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient('localhost', 27017)
db = client['TreeMap']
index_collection = db["TreeDataIndex"]
data_collection = db['TreeData']
users_collection = db['Users']

@app.route('/data/json/<name>', methods=['GET', 'POST'])
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
    



@app.route('/data/delete/<name>', methods=['DELETE'])
def delete_entry(name):
    index_collection.delete_many({'name': name})
    data_collection.delete_many({'name': name})

    return "", 204
    
@app.route('/users/delete/<key>', methods=['DELETE'])
def delete_user(key):
    print(key, users_collection.count_documents({'key' : key}, limit = 1))
    if users_collection.count_documents({'key' : key}, limit = 1) > 0:
        users_collection.delete_many({'key': key})
        return 'Done', 204
    else:
        return 'Not found', 404

@app.route('/users/list', methods=['GET'])
def get_users():
    lst = []
    for document in users_collection.find():
        lst.append({'key': document['key'],  'name': document['name'],  'root': document['root'],  'edit': document['edit'],
                       'creation_date': document['creation_date'],  'last_access': document['last_access']})
    return jsonify(lst)

@app.route('/users/add', methods=['PUT'])
def add_user():
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
        users_collection.update_one({'name' : name}, {"$set": {'key' : key, 'name' : name, 'root' : root, 'edit': edit, 'date_created': str(datetime.datetime.now), 'last_accessed': 'never' }})
        return jsonify({"success": True, "message": "User updated"})
    else:
        users_collection.insert_one({'key' : key, 'name' : name, 'root' : root, 'edit': edit,
                       'creation_date': str(datetime.datetime.now()),  'last_access': 'never'})
        return jsonify({"success": True, "message": "User created"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)