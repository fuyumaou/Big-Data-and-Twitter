#!env/bin/python
from flask import Flask, make_response, jsonify, abort, request, url_for, render_template, session, redirect
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
# !! --- Might be necessary to find alternative way of storing the list of languages
languagesCollection = mongo_db['languages']
tweetsCollection = mongo_db['languageTweets']

# List of languages to be queried on --- built using data from DB
languages=["en","fr","rs"]#sample
for lang in languagesCollection.find():
    languages.append(lang['language'])

# List of all relevant tweets --- built using data from DB
# !! --- might be better to implement querying later on
# !! --- sample for testing (I'm not sure what the database will end up giving us)
tweets = [
    {"x":0,"y":0,"language":"en"},
    {"x":10,"y":50,"language":"fr"}]
for tweet in tweetsCollection.find():
    tweets.append({'language':tweet['language'],'x':tweet['x'],'y':tweet['y']})

#----------------------------------------------------------------------------

# helper_languages_get
# !! --- to be changed to use querying instead of filter
# Input: x0, y0, x1, y1 --- 4 coordinates (west,south,east,north)
# Output: A List of Records of type {language, number} where number is the number
#       of tweets in the respective language in the defined rectangular area
def helper_languages_get(x0, y0, x1, y1):
    results = []
    for lang in languages:
        number_tweets_in_lang=len(filter(lambda p: (p['language']==lang and p['x']>=x0 and p['x']<=x1 and p['y']>=y0 and p['y']<=y1), tweets))
        if number_tweets_in_lang>0:
            results.append([lang,number_tweets_in_lang])
    return results

# helper_languagescircle_get
# !! --- to be changed to use querying instead of filter
# Input: x,y --- 2 coordinates, r --- radius of the area
# Output: A List of Records of type {language, number} where number is the number
#       of tweets in the respective language in the defined circular area
def helper_languagescircle_get(x,y,r):
    results=[]
    for lang in languages:
        number_tweets_in_lang=len(filter(lambda p: (p['language']==lang and (p['x']-x)**2+(p['y']-y)**2<=r**2), tweets))
        if number_tweets_in_lang>0:
            results.append({'language':lang,'number':number_tweets_in_lang})
    return results

# helper_languageslocations_get
# !! --- to be changed to use querying instead of filter
# !! --- naming needs to be changed here and in the actual html doc to be more relevant
# !! --- the naming of this uses geoJSON convention so that it can be used very easily used by google maps(Toby)
# Input: x0, y0, x1, y1 --- 4 coordinates
# Output: A List of Records of type {type, properties:{language}, geometry: {type,coordinates}}
#           that correspond to tweets, their languages and their locations that can be found in the rectangular area x0,y0,x1,y1
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
#           that correspond to tweets, their languages and their locations that can be found in the circular area defined by x,y,r
def helper_languageslocationscircle_get(x,y,r):
    results=[]
    for tweet in (filter(lambda p: ((p['x']-x)**2+(p['y']-y)**2<=r**2), tweets)):
        results.append({'type': 'Feature','properties':{
          'language':tweet['language']}, 'geometry': {'type': 'Point',
            'coordinates': [tweet['x'], tweet['y']]}})
    return results

#----------------------------------------------------------------------------

#----------------------------------------------------------------------------

# GET request for the languages in the rectangular area x0, y0, x1, y1
# ! --- may be worth passing parameters as part of a query string rather than as distinct urls
# ! --- e.g. /languages?x0=0&x1=2&y0=0&y1=1
# ! --- warning, longditude wraps at +/-180 so boxes don't always work
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
    return jsonify({"data":results})

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
    return make_response(jsonify({'type':'LanguagesCounted','features':results}), 200)

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
    return make_response(jsonify({'type':'LanguagesLocations','features':results}),200)

# GET request for the locations of all tweets and their language in circular area with centre (x,y) and radius r**2
@app.route('/languageslocationscircle/<string:sx>/<string:sy>/<string:sr>', methods =['GET'])
def api_languaceslocationscircle_get(sx,sy,r):
    try:
        x = float(sx)
        y = float(sy)
        r = float(sr)
        if (r<0.0):
            raise
    except:
        return make_response(jsonify({'error': 'Bad Request'}), 400)
    results = helper_languageslocationscircle_get(x,y,r)
    return make_response(jsonify({'type':'LanguagesLocations','features':results}),200)

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
