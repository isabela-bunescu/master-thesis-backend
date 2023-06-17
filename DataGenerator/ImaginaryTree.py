import pymongo
import json


def parse_and_write(client):
    name = "imaginary"
    display_name = "Artificially created tree"
    desc = ""

    db = client['TreeMap']
    index = db["TreeDataIndex"]
    data = db['TreeData']

    
    if index.count_documents({'name' : name}, limit = 1) == 0:
      f = open('./DataGenerator/imaginary.json')
      dta = json.load(f)
      index.insert_one({'name' : name, 'display_name' : display_name, 'description' : desc})
      data.insert_one({'name' : name, 'data' : dta})
      print("Dataset %s added in the DB"%(name))
    else:
      print("Dataset %s already in the DB. Skipping..."%(name))