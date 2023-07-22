from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas
 
import pymongo 
app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient('localhost', 27017)
db = client['TreeMap']
index_collection = db["TreeDataIndex"]
data_collection = db['TreeData']

@app.route('/data/json/<name>', methods=['GET', 'POST'])
def generate_json(name):

    c = data_collection.find_one( { 'name': name } )
    return jsonify(c['data'])

@app.route('/data/index', methods=['GET'])
def get_index():
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
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)