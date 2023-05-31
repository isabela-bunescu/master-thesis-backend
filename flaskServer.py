from flask import Flask, jsonify
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


    
if __name__ == '__main__':
    app.run()