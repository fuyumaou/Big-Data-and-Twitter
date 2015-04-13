#!env/bin/python
from flask import Flask, make_response, jsonify, abort, request, url_for, render_template, session, redirect
import os
import pymongo
from pymongo import MongoClient

app = Flask(__name__)
app.config['DEBUG'] = True#Turn debug mode on, the stuff at the bottom doesn't seem to do this. perhaps __name__ isn't '__main__' when using foreman?

# Connecting to Mongo Client
# !! --- Might need to be updated to use a not local DB
mongo_url = os.getenv('MONGOLAB_URI')
mongo_client = MongoClient(mongo_url)
mongo_db = mongo_client.get_default_database()

# Retrieval of languages and tweet collections
languageCollection = mongo_db['languages']

#----------------------------------------------------------------------------
# Language Visualisation specific helper functions:

# get_languages
# Function that retrieves the list of languages to be queried on, built using data from DB
def get_languages():
    language_list=[]
    for lang_tweets in languageCollection.find():
        language_list.append(lang_tweets['language'])
    return language_list

#----------------------------------------------------------------------------
# More general helper functions:

# is_in_rectangle_area
# Function that verifies whether a tweet is within the rectangular area defined by:
# longitudes x0, x1 and latitudes y0, y1.
def is_in_rectangle_area(p,x0,y0,x1,y1):
    ok = True
    if (x0<=x1):
        ok = (x0 <= p['longitude'] and p['longitude'] <= x1)
    else:
        ok = (x0 <= p['longitude'] or p['longitude'] <= x1)
    if (y0<=y1):
        ok = ok and (y0 <= p['latitude'] and p['latitude'] <= y1)
    else:
        raise
    return ok

# is_within_distance
# Function that verifies whether a tweet is within the distance r**2 from the point (x,y).
# Input: longitude x, latitude y, root of distance r
# !! --- Not Certain if this is how distances are computed using longitude and latitude
def is_within_distance(p,x,y,r):
    return (p['longitude']**2 + p['latitude']**2 <= r**2)

# is_in_circle_area
# Function that verifies whether a tweet is within the circular area defined by:
# centre of longitude x and latitude y, and radius r
# !! --- Allows wrapping on longitude, but not on latitude!!
def is_in_circle_area(p,x,y,r):
    ok = True
    for i in [-180,0,180]:
            ok = ok and is_within_distance(p,x+i,y,r)
    return ok

#----------------------------------------------------------------------------
# Helper functions for GET Requests:

# helper_languages_get
# !! --- to be changed to use querying instead of len+filter
# !! --- querying might not be possible ?
# Input: x0, y0, x1, y1 --- 4 coordinates (west,south,east,north)
# Output: A List of Records of type {language, number} where number is the number
#       of tweets in the respective language in the defined rectangular area
def helper_languages_get(x0, y0, x1, y1):
    languages = get_languages()
    results = []
    for lang in languages:
        lang_tweets = languageCollection.find_one({'language':lang})
        number_tweets_in_lang = len(filter(lambda p: is_in_rectangle_area(p,x0,y0,x1,y1), lang_tweets['tweet']))
        if number_tweets_in_lang>0:
            results.append([lang,number_tweets_in_lang])
    return results

# helper_languagescircle_get
# !! --- to be changed to use querying instead of len+filter
# !! --- querying might not be possible ?
# Input: x,y --- 2 coordinates, r --- radius of the area
# Output: A List of Records of type {language, number} where number is the number
#       of tweets in the respective language in the defined circular area
def helper_languagescircle_get(x,y,r):
    languages = get_languages()
    results=[]
    for lang in languages:
        lang_tweets = languageCollection.find_one({'language':lang})
        number_tweets_in_lang = len(filter(lambda p: is_in_circle_area(p,x,y,r), lang_tweets['tweet']))
        if number_tweets_in_lang>0:
            results.append({'language':lang,'number':number_tweets_in_lang})
    return results

# helper_languageslocations_get
# !! --- to be changed to use querying instead of filter
# !! --- querying might not be possible ?
# !! --- the naming of this uses geoJSON convention so that it can be used very easily used by google maps(Toby)
# Input: x0, y0, x1, y1 --- 4 coordinates
# Output: A List of Records of type {type, properties:{language}, geometry: {type,coordinates}}
#           that correspond to tweets, their languages and their locations that can be found in the rectangular area x0,y0,x1,y1
def helper_languageslocations_get(x0,y0,x1,y1):
    languages = get_languages()
    results = []
    for lang in languages:
        lang_tweets = languageCollection.find_one({'language':lang})
        for tweet in filter(lambda p: is_in_rectangle_area(p,x0,y0,x1,y1), lang_tweets['tweet']):
            results.append({
				'type': 'Feature',
				'properties': {
					'language':lang
				}, 'geometry': {
					'type': 'Point',
					'coordinates': [tweet['longitude'], tweet['latitude']]
				}
			})
    return results

# helper_languageslocationscircle_get
# !! --- to be changed to use querying instead of filter
# !! --- querying might not be possible ?
# Input: x,y --- 2 coordinates, r --- radius of the area
# Output: A List of Records of type {type, properties:{language}, geometry: {type,coordinates}}
#           that correspond to tweets, their languages and their locations that can be found in the circular area defined by x,y,r
def helper_languageslocationscircle_get(x,y,r):
    languages = get_languages()
    results=[]
    for lang in languages:
        lang_tweets = languageCollection.find_one({'language':lang})
        for tweet in filter(lambda p: is_in_circle_area(p,x,y,r), lang_tweets['tweet']):
            results.append({'type': 'Feature','properties':{
              'language':lang}, 'geometry': {'type': 'Point',
                'coordinates': [tweet['longitude'], tweet['latitude']]}})
    return results

#----------------------------------------------------------------------------

#----------------------------------------------------------------------------

# GET request for the languages in the rectangular area x0, y0, x1, y1
# ! --- may be worth passing parameters as part of a query string rather than as distinct urls
# ! --- e.g. /languages?x0=0&x1=2&y0=0&y1=1
@app.route('/languages/<string:sx0>/<string:sy0>/<string:sx1>/<string:sy1>', methods = ['GET'])
def api_languages_get(sx0,sy0,sx1,sy1):
    try:
        x0 = float(sx0)
        y0 = float(sy0)
        x1 = float(sx1)
        y1 = float(sy1)
    except:
        return make_response(jsonify({'error': 'Bad Request'}), 400)
    results = helper_languages_get(x0,y0,x1,y1)
    return make_response(jsonify({'type':'LanguagesCounted','data':results}), 200)

# GET request for the languages in the circular area with centre (x, y) and radius r
@app.route('/languagescircle/<string:sx>/<string:sy>/<string:sr>', methods = ['GET'])
def api_languagescircle_get(sx,sy,sr):
    try:
        x = float(sx)
        y = float(sy)
        r = float(sr)
        if (r<0.0):
            raise
    except:
        return make_response(jsonify({'error': 'Bad Request'}), 400)
    results = helper_languagescircle_get(x,y,r)
    return make_response(jsonify({'type':'LanguagesCounted','data':results}), 200)

# GET request for the locations of all tweets and their language in the rectangular area x0, y0, x1, y1
@app.route('/languageslocations/<string:sx0>/<string:sy0>/<string:sx1>/<string:sy1>', methods = ['GET'])
def api_languageslocations_get(sx0,sy0,sx1,sy1):
    try:
        x0 = float(sx0)
        y0 = float(sy0)
        x1 = float(sx1)
        y1 = float(sy1)
    except:
        return make_response(jsonify({'error': 'Bad Request'}), 400)
    results = helper_languageslocations_get(x0,y0,x1,y1)
    return make_response(jsonify({'type':'LanguagesLocations','data':results}),200)

# GET request for the locations of all tweets and their language in circular area with centre (x,y) and radius r**2
@app.route('/languageslocationscircle/<string:sx>/<string:sy>/<string:sr>', methods =['GET'])
def api_languaceslocationscircle_get(sx,sy,sr):
    try:
        x = float(sx)
        y = float(sy)
        r = float(sr)
        if (r<0.0):
            raise
    except:
        return make_response(jsonify({'error': 'Bad Request'}), 400)
    results = helper_languageslocationscircle_get(x,y,r)
    return make_response(jsonify({'type':'LanguagesLocations','data':results}),200)

# An actual webpage!!
@app.route('/')
def homepage_get():
    return render_template("map.html")

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
