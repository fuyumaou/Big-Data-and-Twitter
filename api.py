#!env/bin/python
from flask import Flask, make_response, jsonify, abort, request, url_for, render_template, session, redirect
import pymongo
from pymongo import MongoClient
app = Flask(__name__)
# Connecting to Mongo Client
# !! --- Might need to be updated to use a not local DB
client = MongoClient()

# Connecting to Mock Database
# !! --- To be updated to deal with the actual DBs
db = client['MockDB']

# Retrieval of languages and tweet collections
# !! --- Might be necessary to find alternative way of storing the list of languages
languagesCollection = db['languageList']
tweetsCollection = db['languageTweets']

# List of languages to be queried on --- built using data from DB
languages=[]
for lang in languagesCollection.find():
	languages.append(lang['language'])

# List of all relevant tweets --- built using data from DB
# !! --- might be better to implement querying later on
tweets=[]
for tweet in tweetsCollection.find():
	tweets.append({'language':tweet['language'],'x':tweet['x'],'y':tweet['y']})
#----------------------------------------------------------------------------

# helper_languages_get
# !! --- to be changed to use querying instead of filter
# Input: x0, y0, x1, y1 --- 4 coordinates
# Output: A List of Records of type {language, number} where number is the number
#		of tweets in the respective language in the defined rectangular area
def helper_languages_get(x0,y0,x1,y1):
	results=[]
	for lang in languages:
		number_tweets_in_lang=len(filter(lambda p: (p['language']==lang and p['x']>=x0 and p['x']<=x1 and p['y']>=y0 and p['y']<=y1), tweets))
		if len>0:
			results.append({'language':lang,'number':number_tweets_in_lang})
	return results
	
# helper_languagescircle_get
# !! --- to be changed to use querying instead of filter
# Input: x,y --- 2 coordinates, r --- radius of the area
# Output: A List of Records of type {language, number} where number is the number
#		of tweets in the respective language in the defined circular area
def helper_languagescircle_get(x,y,r):
	results=[]
	for lang in languages:
		number_tweets_in_lang=len(filter(lambda p: (p['language']==lang and (p['x']-x)**2+(p['y']-y)**2<=r**2), tweets))
		if len>0:
			results.append({'language':lang,'number':number_tweets_in_lang})
	return results

# helper_languageslocations_get
# !! --- to be changed to use querying instead of filter
# !! --- naming needs to be changed here and in the actual html doc to be more relevant
# Input: x0, y0, x1, y1 --- 4 coordinates
# Output: A List of Records of type {type, properties:{language}, geometry: {type,coordinates}}
#			that correspond to tweets, their languages and their locations that can be found in the rectangular area x0,y0,x1,y1
def helper_languageslocations_get(x0,y0,x1,y1):
	results=[]
	for tweet in (filter(lambda p: (p['x']>=x0 and p['x']<=x1 and p['y']>=y0 and p['y']<=y1),tweets)):
		results.append({'type': 'Feature','properties':{
		  'language':tweet['language']}, 'geometry': {'type': 'Point',
		    'coordinates': [tweet['x'], tweet['y']]}})
	return results
	
# helper_languageslocationscircle_get
# !! --- to be changed to use querying instead of filter
# !! --- naming needs to be changed here and in the actual html doc to be more relevant
# Input: x,y --- 2 coordinates, r --- radius of the area
# Output: A List of Records of type {type, properties:{language}, geometry: {type,coordinates}}
#			that correspond to tweets, their languages and their locations that can be found in the circular area defined by x,y,r
def helper_languageslocationscircle_get(x,y,r):
	results=[]
	for tweet in (filter(lambda p: ((p['x']-x)**2+(p['y']-y)**2<=r**2), tweets)):
		results.append({'type': 'Feature','properties':{
		  'language':tweet['language']}, 'geometry': {'type': 'Point',
		    'coordinates': [tweet['x'], tweet['y']]}})
	return results

#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# !! --- NEGATIVE VALUES ARE NOT SUPPORTED YET!!!!!

# GET request for the languages in the rectangular area x0, y0, x1, y1
@app.route('/languages/<int:x0>/<int:y0>/<int:x1>/<int:y1>', methods = ['GET'])
def api_languages_get(x0,y0,x1,y1):
	results = helper_languages_get(x0,y0,x1,y1)
	return make_response(jsonify({'type':'LanguagesCounted','features':results}), 200)

# GET request for the languages in the circular area with centre (x, y) and radius r
@app.route('/languagescircle/<int:x>/<int:y>/<int:r>', methods = ['GET'])
def api_languagescircle_get(x,y,r):
	results = helper_languagescircle_get(x,y,r)
	return make_response(jsonify({'type':'LanguagesCounted','features':results}), 200)
	
# GET request for the locations of all tweets and their language in the rectangular area x0, y0, x1, y1
@app.route('/languageslocations/<int:x0>/<int:y0>/<int:x1>/<int:y1>', methods = ['GET'])
def api_languageslocations_get(x0,y0,x1,y1):
	results = helper_languageslocations_get(x0,y0,x1,y1)
	return make_response(jsonify({'type':'LanguagesLocations','features':results}),200)
	
# GET request for the locations of all tweets and their language in circular area with centre (x,y) and radius r**2
@app.route('/languageslocationscircle/<float:x>/<float:y>/<float:r>', methods =['GET'])
def api_languaceslocationscircle_get(x,y,r):
	results = helper_languageslocationscircle_get(x,y,r)
	return make_response(jsonify({'type':'LanguagesLocations','features':results}),200)

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------

# Handler for 404 errors
@app.errorhandler(404)
def error_not_found(error):
	return make_response(jsonify({'error': 'Resource not found'}), 404)

#-----------------------------------------------------------------------------
#Debug mode ON
if __name__ == '__main__':
	app.run(debug = True)