import os 
from pymongo import MongoClient, GEOSPHERE

# Current DB Model Conversion Script --- BE CAREFUL WHILE USING OR EDITING!!!!!

# Connecting to Mongo Client
mongo_url = os.getenv('MONGOLAB_URI')
mongo_client = MongoClient(mongo_url)
mongo_db = mongo_client.get_default_database()

#creating temporary collection
oldLanguageCollection = mongo_db['languages']
newLanguageCollection = mongo_db['languages0']

# move to temporary collection
for lang in oldLanguageCollection.find():
    tweets = lang['tweet']
    for tw in tweets:
        newLanguageCollection.insert({'language':lang['language'],'tweet':[tw['longitude'],tw['latitude']]})