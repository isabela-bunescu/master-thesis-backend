from . import CountryData
from . import ImaginaryTree
from . import CountryDataModified
import pymongo
import datetime

client = pymongo.MongoClient('localhost', 27017)

CountryData.parse_and_write(client)

CountryDataModified.parse_and_write(client)

ImaginaryTree.parse_and_write(client)

db = client['TreeMap']
index_users = db["Users"]
index_users.insert_one({'key': 'root_key',  'name': 'Default root user',  'root': True,  'edit': True,
                       'creation_date': str(datetime.datetime.now()),  'last_access': 'never'})
