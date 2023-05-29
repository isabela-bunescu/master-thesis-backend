import pymongo 

client = pymongo.MongoClient('localhost', 27017)

from . import CountryData 
CountryData.parse_and_write(client)
