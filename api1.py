#!env/bin/python
from flask import Flask, make_response, jsonify, abort, request, url_for, render_template, session, redirect
import os
from pymongo import MongoClient, GEOSPHERE
from TwitterAPI import TwitterAPI

app = Flask(__name__)
app.config['DEBUG'] = True#Turn debug mode on, the stuff at the bottom doesn't seem to do this. perhaps __name__ isn't '__main__' when using foreman?

# Twitter API connection
twitter_access_token = '178658388-CDwtvkSOOb3ikZXaVeDBlxzHwj0wEyQ5ntTPhs5n'
twitter_access_token_secret = 'zJzQK6F00hwsG32STbITqvavbhYt5rtV6vZH69QbcKf8I'
twitter_consumer_key = 'bWMmJpHklikmU3fbKemgmr40H'
twitter_consumer_secret = 'MsAYHkqUuGi1bBWiTyiJiDdVCQ6DvYMt8ROsjJ1GFIFQCFP0Dp'
twitter_api = TwitterAPI(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)

# Connecting to Mongo Client
mongo_url = os.getenv('MONGOLAB_URI')
mongo_client = MongoClient(mongo_url)
mongo_db = mongo_client.get_default_database()

# Retrieval of languages and tweet collections
languageCollection = mongo_db['languages0']
wordsCollection = mongo_db['words0']

#----------------------------------------------------------------------------
# Language Visualisation specific helper functions:

# can we avoid calling this too often? surely language_list won't change much?
# get_languages
# Function that retrieves the list of languages to be queried on, built using data from DB
def get_language_list():
	return languageCollection.distinct('language')

#----------------------------------------------------------------------------
# Helper functions for GET Requests:

# helper_language_tweets_count
# Input: x0, y0, x1, y1 --- 4 coordinates (west,south,east,north)
# Output: A List of Records of type {language, number} where number is the number
#	   of tweets in the respective language in the defined rectangular area
def helper_language_tweets_count(x0, y0, x1, y1):
	languages = get_language_list()
	results = []
	for lang in languages:
		number_tweets_in_lang = languageCollection.find({
			'location': {
				'$within': {
					'$box': [[x0, y0], [x1, y1]]
				}
			},
			'language': lang
		}).count()
		if number_tweets_in_lang > 0:
			results.append([lang, number_tweets_in_lang])

	return results

# helper_language_tweet_locations
# !! --- the naming of this uses geoJSON convention so that it can be used very easily used by google maps(Toby)
# Input: x0, y0, x1, y1 --- 4 coordinates
# Output: A List of Records of type {type, properties:{language}, geometry: {type,coordinates}}
#		   that correspond to tweets, their languages and their locations that can be found in the rectangular area x0,y0,x1,y1
def helper_language_tweet_locations(x0,y0,x1,y1):
	results = []
	for tweet in languageCollection.find({'location':{'$within':{'$box': [[x0,y0],[x1,y1]]}}}):
		results.append({
			'type': 'Feature',
			'properties': {
				'language':tweet['language']
			}, 'geometry': {
				'type': 'Point',
				'coordinates': tweet['location']
			}
		})
	return results

# helper_words_get
# Input: sw_longitude, sw_latitude, ne_longitude, ne_latitude, words_count
# Output: The List of the words_count pairs of most frequent words and their count for the given area
def helper_words_get(sw_longitude, sw_latitude, ne_longitude, ne_latitude, word_count):
	words = {}
	for tweet in wordsCollection.find({'location':{'$within':{'$box': [[sw_longitude, sw_latitude],[ne_longitude, ne_latitude]]}}}):
		word = tweet['word']
		if word not in words:
			words[word] = 0
		words[word]+=1

	word_list = []
	for word in words:
		word_list.append({
			'word': word,
			'count': words[word]
		})

	word_list.sort(key = lambda w: w['count'], reverse = True)

	return word_list[:word_count]


#----------------------------------------------------------------------------

#----------------------------------------------------------------------------

# GET request for the languages in the rectangular area x0, y0, x1, y1
@app.route('/languages/<string:sx0>/<string:sy0>/<string:sx1>/<string:sy1>', methods = ['GET'])
def api_languages_get(sx0,sy0,sx1,sy1):
	try:
		x0 = float(sx0)
		y0 = float(sy0)
		x1 = float(sx1)
		y1 = float(sy1)
	except:
		abort(400)
	results = helper_language_tweets_count(x0,y0,x1,y1)
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
		abort(400)
	results = helper_language_tweet_locations(x0,y0,x1,y1)
	return make_response(jsonify({'type':'FeatureCollection','features':results}),200)

# GET request for the first word_count meaningful words and their language in the rectangular area defined by sw_longitude, sw_latitude, ne_longitude, ne_latitude
@app.route('/words/<string:sw_longitude>/<string:sw_latitude>/<string:ne_longitude>/<string:ne_latitude>/<int:word_count>', methods = ['GET'])
def api_words_get(sw_longitude, sw_latitude, ne_longitude, ne_latitude, word_count):
	try:
		sw_longitude = float(sw_longitude)
		sw_latitude = float(sw_latitude)
		ne_longitude = float(ne_longitude)
		ne_latitude = float(ne_latitude)
	except:
		abort(400)
	results = helper_words_get(sw_longitude, sw_latitude, ne_longitude, ne_latitude, word_count);
	return make_response(jsonify({'words': results}), 200)

@app.route('/place/<string:place>', methods = ['GET'])
def api_place(place):
	tweets_request = twitter_api.request('search/tweets', { 'q': place })
	tweets = []
	for tweet in tweets_request:
		tweets.append(tweet)
	return make_response(jsonify({ 'tweets': tweets }))

#-----------------------------------------------------------------------------

@app.route('/')
def homepage_get():
	return render_template("map.html")

#-----------------------------------------------------------------------------

# Handler for 400 (bad request) errors
@app.errorhandler(400)
def error_not_found(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

# Handler for 404 (not found) errors
@app.errorhandler(404)
def error_not_found(error):
	return make_response(jsonify({'error': 'Resource not found'}), 404)

#-----------------------------------------------------------------------------
#Debug mode ON
if __name__ == '__main__':
	app.run(debug = True)
