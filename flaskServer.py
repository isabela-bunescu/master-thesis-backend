from flask import Flask, jsonify, request, session
from flask_cors import CORS
import pandas
import datetime 
import json 
import pymongo 

import os 
try:
    host_db = os.environ['DB_HOST']
except:
    host_db = 'localhost'
try:
    user_db = os.environ['DB_USER']
except:
    user_db = ''
try:
    pass_db = os.environ['DB_PASS']
except:
    pass_db = ''
try:
    port_db = os.environ['DB_PORT']
except:
    port_db = '27017'
    

# app setup
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)
# db setup     
client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/'%(user_db, pass_db, host_db, port_db) if len(user_db)>0 else 'mongodb://%s:%s/'%(host_db, port_db))
db = client['TreeMap']
index_collection = db["TreeDataIndex"]
data_collection = db['TreeData']
users_collection = db['Users']

def is_valid_data_id(s):
    """
    Check if a given string is a valid data ID.

    Parameters:
    - s (str): The string to be checked as a data ID.

    Returns:
    - bool: True if the string is a valid data ID, False otherwise.
    """

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
    """
    Retrieves JSON data associated with the given name.

    Parameters:
        name (str): The name used to identify the JSON data.

    Returns:
        JSON response: A JSON object containing the data associated with the provided name.

    Raises:
        Unauthorized (401): If the user is not logged in or authenticated.
    """

    if 'log_in' in session and session['log_in']:
        c = data_collection.find_one( { 'name': name } )
        return jsonify(c['data'])
    else:
        return "Only users can access this",  401
        

@app.route('/data/index', methods=['GET'])
def get_index():
    """
    Get all the Index entres from the database and sends them to the clinet.

    Returns:
        json: the json containing the list of entries.
    """
    if 'log_in' in session and session['log_in']:
        lst = []
        for document in index_collection.find():
            lst.append({'name' : document['name'], 'display_name' : document['display_name'], 'description' : document['description']})
        return jsonify(lst)
    else:
        return "Only users can access this",  401

@app.route('/data/index', methods=['PUT'])
def update_index():
    """
    Update an existing index entry in the database.

    Returns:
        json: A JSON response indicating the success of the operation.
    """
    if 'log_in' in session and session['log_in'] and session['edit']:
        try:
            name = request.json['name']
            display_name = request.json['display_name']
            description = request.json['description']
        except:
            return jsonify({"success": False})

        if index_collection.count_documents({'name' : name}, limit=1) > 0:
            # Update the existing index entry
            index_collection.update_one(
                {'name': name},
                {"$set": {'name': name, 'display_name': display_name, 'description': description}}
            )
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    else:
        return "Either not authenticated or the user has no edit rights", 401
    
@app.route('/data/index', methods=['POST'])
def add_index():
    """
    Add an index entry to the database.

    Returns:
        json: Success message if the index entry is added successfully, error message otherwise.
    """

    if 'log_in' in session and session['log_in'] and session['edit']:
        try:
            name = str(request.json['name'])
            display_name = request.json['display_name']
            description = request.json['description']

            if len(display_name) == 0:
                return jsonify({"success": False, "message": "Display name should contain at least one character"})

            if not is_valid_data_id(name):
                return jsonify({"success": False, "message": "Must contain only characters 0-9, a-z, A-Z, '_', '-'"})
        except:
            return jsonify({"success": False, "message": "Something went wrong"})

        if index_collection.count_documents({'name': name}, limit=1) > 0:
            return jsonify({"success": False, "message": "Index already exists"})
        else:
            index_collection.insert_one({'name': name, 'display_name': display_name, 'description': description})
            data_collection.insert_one({'name': name, 'data': []})
            return jsonify({"success": True, "message": "Index added"})

    else:
        return "Either not authenticated or the user has no edit rights", 401
    
@app.route('/data/json/<name>', methods=['PUT'])
def update_json(name):
    """
    Updates the JSON data associated with a specific name.

    Parameters:
        name (str): The name of the entry to update.

    Returns:
        If the user is authenticated and has edit rights:
            - If the entry exists, updates its data and returns a JSON response with {"success": True}.
            - If the entry does not exist, returns a JSON response with {"success": False}.

        If the user is not authenticated or does not have edit rights, returns an error message and status code 401.

    """

    # Check if the user is authenticated and has edit rights
    if 'log_in' in session and session['log_in'] and session['edit']:

        # Load the JSON data from the request
        data = json.loads(str(request.json['data']))

        # Check if the entry exists in the collection
        if data_collection.count_documents({'name': name}, limit=1) == 1:

            # Update the entry data
            data_collection.update_one({'name': name}, {"$set": {'name': name, 'data': data}})

            return jsonify({"success": True})

        return jsonify({"success": False})

    else:
        return "Either not authenticated or the user has no edit rights", 401

@app.route('/data/delete/<name>', methods=['DELETE'])
def delete_entry(name):
    """
    Deletes an entry from the database based on the provided name.

    Parameters:
        name (str): The name of the entry to be deleted.

    Returns:
        str: An empty string with a status code of 204 if the deletion is successful.
             Otherwise, returns an error message with a status code of 401.

    """
    if 'log_in' in session and session['log_in'] and session['edit']:
        # Check if the user is logged in and has edit rights
        # Delete the entries matching the provided name from index_collection and data_collection
        index_collection.delete_many({'name': name})
        data_collection.delete_many({'name': name})

        return "", 204  # Successful deletion, returns an empty response with status code 204
    else:
        return "Either not authenticated or the user has no edit rights", 401
        # Unauthorized access, returns an error message with status code 401

        
## Users 
@app.route('/users/delete/<key>', methods=['DELETE'])
def delete_user(key):
    """
    Deletes a user from the database.

    Parameters:
        key (str): The key or identifier of the user to be deleted.

    Returns:
        str: A message indicating the status of the deletion.

    """

    if 'log_in' in session and session['log_in'] and session['root']:
        # Check if the user has root privileges
        if users_collection.count_documents({'key': key}, limit=1) > 0:
            # If user with given key exists, delete the user
            document = next(users_collection.find({'key' : key}))
            if document['name'] == "Default root user":
                return 400, "No one can delete the main root user"
            if key == session['key']:
                session['log_in'] = False
            users_collection.delete_many({'key': key})
            return 'Done', 204
        else:
            # If user with given key does not exist, return 'Not found'
            return 'Not found', 404
    else:
        # If user is not logged in or does not have root privileges
        if 'log_in' in session and session['log_in'] and not session['root']:
            # Return 'Don't have permission' if logged in but without root privileges
            return "Don't have permission", 400
        else:
            # Return 'Login required' if not logged in
            return "Login required", 400
        
        
@app.route('/users/list', methods=['GET'])
def get_users():
    """
    Get the list of users from the database.

    Returns:
        json: The JSON response containing the list of users.

    Raises:
        HTTPException: If there is an error or the user does not have the required permissions.
    """

    lst = []

    if 'log_in' in session and session['log_in'] and session['root']:
        for document in users_collection.find():
            lst.append({
                'key': document['key'],
                'name': document['name'],
                'root': document['root'],
                'edit': document['edit'],
                'creation_date': document['creation_date'],
                'last_access': document['last_access']
            })

        return jsonify(lst)
    else:
        if 'log_in' in session and session['log_in'] and not session['root']:
            raise HTTPException("Don't have permission", 400)
        else:
            raise HTTPException("Login required", 400)

@app.route('/users/add', methods=['PUT'])
def add_user():
    """
    Adds or updates user information in the system.

    Returns:
        A JSON response containing success status and a message.

    Raises:
        400 Bad Request: If there is an error or insufficient permissions.

    """

    if 'log_in' in session and session['log_in'] and session['root']:
        # Check if the user is logged in and has root access
        try:
            key = str(request.json['key'])
            name = str(request.json['name'])
            root = bool(request.json['root'])
            edit = bool(request.json['edit'])

            # Validate the key and name inputs
            if len(key) < 6 or not key.isalnum():
                return jsonify({"success": False, "message": "key must contain at least 6 characters (a-z, A-Z, 0-9)"})
            if len(name) < 3:
                return jsonify({"success": False, "message": "name must be at least 3 characters long"})

            # Set edit to True if root is True
            if root:
                edit = True

        except:
            return jsonify({"success": False, "message": "Invalid form data"})

        if users_collection.count_documents({'key': key}, limit=1) > 0:
            # Update existing user
            users_collection.update_one({'key': key}, {"$set": {'key': key, 'name': name, 'root': root, 'edit': edit,
                                                                 'date_created': str(datetime.datetime.now()),
                                                                 'last_accessed': 'never'}})
            return jsonify({"success": True, "message": "User updated"})
        else:
            # Insert new user
            users_collection.insert_one({'key': key, 'name': name, 'root': root, 'edit': edit,
                                         'creation_date': str(datetime.datetime.now()), 'last_access': 'never'})
            return jsonify({"success": True, "message": "User created"})
    else:
        if 'log_in' in session and session['log_in'] and not session['root']:
            # User does not have permission to perform the operation
            return "Don't have permission", 400
        else:
            # User needs to log in
            return "Login required", 400

@app.route('/users/login', methods=['POST'])
def login():
    """
    Handle user login request.

    This function handles the POST request to the '/users/login' endpoint and performs user authentication
    based on the provided 'key' in the JSON payload. It sets session variables based on the retrieved user 
    document from a MongoDB collection.

    Returns:
        A JSON response indicating the success status.
    """
    print('mongodb://%s:%s@%s:%s/'%(user_db, pass_db, host_db, port_db) if len(user_db)>0 else 'mongodb://%s:%s/'%(host_db, port_db))

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
                session['key'] = document['key']
                session['log_in'] = True
                users_collection.update_one({'key': key}, {"$set": {'last_accessed': str(datetime.datetime.now())}})
                return jsonify({"success": True, "message": "",  "root": document['root'], "edit": document['edit'], "name": document['name']})
            except:
                return jsonify({"success": False, "message": "Error occured", "root": False, "edit": False})
        else:
            return jsonify({"success": False, "message": "Invalid key", "root": False, "edit": False})
    except:
        return "Format error", 400


@app.route('/users/check_login', methods=['GET'])
def check_login():
    """
    Checks if a user is currently logged in and returns relevant session information.

    Returns:
        A JSON response containing the success status, message, user name, edit rights, and root status.
            - If a user is logged in, the success status is True, and the message is empty.
              The JSON response also includes the user's name, edit rights, and root status.
            - If no user is logged in, the success status is False, and the message is "No user login".
              The other fields (name, edit, root) are set to default values.

    """

    if 'log_in' in session and session['log_in']:
        return jsonify({"success": True, "message": "", "name": session['name'], "edit": session['edit'], "root": session['root']})
    else:
        return jsonify({"success": False, "message": "No user login", "name": "", "edit": False, "root": False})


@app.route('/users/logout', methods=['GET'])
def logout():
    """
    Logs out the user by setting 'log_in' attribute in the session to False.

    Returns:
        A HTTP response with a status code 204 (No Content) if the user was logged in.
        A HTTP response with a status code 404 (Not Found) if there was no active user session.

    """

    if 'log_in' in session and session['log_in'] == True:
        session['log_in'] = False
        return "", 204
    else:
        return "", 404
    
if __name__ == '__main__':

    app.run(debug=False, host='0.0.0.0', port=5000)
