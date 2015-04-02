#!env/bin/python
from flask import Flask, make_response, jsonify, abort, request, url_for, render_template, session, redirect
app = Flask(__name__)

#Mock Database --- to be replaced with actual DB
db = [
	 {'id':1,'language':'en','x':1,'y':1},
	 {'id':2,'language':'en','x':2,'y':2},
	 {'id':3,'language':'rs','x':3,'y':0}
	]

#List of languages to be queried on
# !! --- Update it to contain all languages in one way or another OR Sort the DB on languages OR implement any other solution for the helper
languages = ['en']

#----------------------------------------------------------------------------

# helper_languages_get
# !! --- need to be changed to work with an actual MongoDB database
# Input: x0, y0, x1, y1 --- 4 coordinates
# Output: A List of Records of type {language, number} where number is the number
#		of tweets in the respective language in the defined rectangular area
def helper_languages_get(x0,y0,x1,y1):
	results=[]
	for lang in languages:
		number_tweets_in_lang=len(filter(lambda p: (p['language']==lang and p['x']>=x0 and p['x']<=x1 and p['y']>=y0 and p['y']<=y1), db))
		if len>0:
			results.append({'language':lang,'number':number_tweets_in_lang})
	return results
	
# helper_languagescircle_get
# !! --- need to be changed to work with an actual MongoDB database
# Input: x,y --- 2 coordinates, r --- radius of the area
# Output: A List of Records of type {language, number} where number is the number
#		of tweets in the respective language in the defined circular area
def helper_languagescircle_get(x,y,r):
	results=[]
	for lang in languages:
		number_tweets_in_lang=len(filter(lambda p: (p['language']==lang and (p['x']-x)**2+(p['y']-y)**2<=r**2), db))
		if len>0:
			results.append({'language':lang,'number':number_tweets_in_lang})
	return results

# helper_languageslocations_get
# !! --- need to be changed to work with an actual MongoDB database
# !! --- naming needs to be changed here and in the actual html doc to be more relevant
# Input: x0, y0, x1, y1 --- 4 coordinates
# Output: A List of Records of type {type, properties:{language}, geometry: {type,coordinates}}
#			that correspond to tweets, their languages and their locations that can be found in the rectangular area x0,y0,x1,y1
def helper_languageslocations_get(x0,y0,x1,y1):
	results=[]
	for tweet in (filter(lambda p: (p['x']>=x0 and p['x']<=x1 and p['y']>=y0 and p['y']<=y1),db)):
		results.append({'type': 'Feature','properties':{
		  'language':tweet['language']}, 'geometry': {'type': 'Point',
		    'coordinates': [tweet['x'], tweet['y']]}})
	return results
	
# helper_languageslocationscircle_get
# !! --- need to be changed to work with an actual MongoDB database
# !! --- naming needs to be changed here and in the actual html doc to be more relevant
# Input: x,y --- 2 coordinates, r --- radius of the area
# Output: A List of Records of type {type, properties:{language}, geometry: {type,coordinates}}
#			that correspond to tweets, their languages and their locations that can be found in the circular area defined by x,y,r
def helper_languageslocationscircle_get(x,y,r):
	results=[]
	for tweet in (filter(lambda p: ((p['x']-x)**2+(p['y']-y)**2<=r**2), db)):
		results.append({'type': 'Feature','properties':{
		  'language':tweet['language']}, 'geometry': {'type': 'Point',
		    'coordinates': [tweet['x'], tweet['y']]}})
	return results

#----------------------------------------------------------------------------

#----------------------------------------------------------------------------

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
@app.route('/languageslocationscircle/<int:x>/<int:y>/<int:r>', methods =['GET'])
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
if __name__ == '__main__':
	app.run(debug = True)