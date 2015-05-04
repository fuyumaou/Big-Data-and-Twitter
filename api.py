#!env/bin/python
from flask import Flask, make_response, jsonify, abort, request, url_for, render_template, session, redirect
import os
import math
import requests
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

# MongoDB collections
languageCollection = mongo_db['languages0']
wordsCollection = mongo_db['words0']

# Retrieves the list of all languages to be queried on
def get_language_list():
	return languageCollection.distinct('language')

# Get the geolocation of a tweet or return None on failure
def helper_tweet_geolocation(tweet):
	if 'coordinates' in tweet:
		geo = tweet['coordinates']
		if geo is not None and 'type' in geo and geo['type'] == 'Point' and 'coordinates' in geo:
			coordinates = geo['coordinates']
			return (coordinates[1], coordinates[0])
		return None
	else:
		return None

# Get list of images of a tweet
def helper_tweet_images(tweet):
	images = []
	if 'entities' in tweet and 'media' in tweet['entities']:
		media = tweet['entities']['media']
		for item in media:
			if 'type' in item and item['type'] == 'photo' and 'media_url_https' in item:
				images.append(item['media_url_https'])
	return images

# Get the Twitter account id of a tweet or return None on failure
def helper_tweet_account_id(tweet):
	if 'user' in tweet and 'id' in tweet['user']:
		return tweet['user']['id']
	return None

# Get the distance in km between two places on Earth
def helper_distance_km(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi / 180.0
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    cos = math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) + math.cos(phi1) * math.cos(phi2)
    arc = math.acos(cos)
    return arc * 6373.0

# Get the sentiment score of a tweet between -1.0 and 1.0 or return None on failure
def helper_tweet_sentiments(tweet):
	alchemy_url = "http://access.alchemyapi.com/calls/text/TextGetTextSentiment"
	parameters = {
		"apikey" : '939a194dc9ac063a2c2a89358276a7e4e626b4e7',
		"text"   : tweet['text'],
		"outputMode" : "json",
		"showSourceText" : 1
	}

	try:
		results = requests.get(url = alchemy_url, params = parameters)
		response = results.json()
	except Exception as e:
		return None

	try:
		if 'OK' != response['status'] or 'docSentiment' not in response:
			return None
		tweet['sentiment'] = response['docSentiment']['type']
		score = 0.0
		if tweet['sentiment'] in ('positive', 'negative'):
			score = float(response['docSentiment']['score'])
		return score
	except Exception as e:
		return None

	return None

# Retrieve a tweet count for each language in a rectangular area
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

# Retrieve a tweet count for each language in a circular area
def helper_language_tweet_circle_count(x, y, r):
    languages = get_language_list()
    results = []
    for lang in languages:
        number_tweets_in_lang = languageCollection.find({
            'location': {
                '$geoWithin': {
                    '$centerSphere': [[x, y], r]
                }
            },
            'language': lang
        }).count()
        if number_tweets_in_lang > 0:
            results.append([lang, number_tweets_in_lang])
    return results

# Retrieve tweets' coordinates and language in a rectangular area
def helper_language_tweet_locations(x0, y0, x1, y1):
	results = []
	tweets = languageCollection.find({
		'location': {
			'$within': {
				'$box': [[x0, y0],[x1, y1]]
			}
		}
	})
	for tweet in tweets:
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

# Retrieve the most frequent words and the number of tweets in which they appear in a rectangular area
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

# Retrieve the official account of a place from Twitter
def helper_place_account(place):
	account_id = None
	account_name = None
	r = twitter_api.request('users/search', {'q': place})
	for account in r:
		if 'verified' in account and 'id_str' in account and account['verified'] == True:
			account_id = account['id_str']
			if 'name' in account:
				account_name = account['name']
			break
	return (account_id, account_name)

# Retrieve a list of tweets of an account from Twitter
def helper_place_account_tweets(acount):
	account_tweets = []
	if acount is not None:
		r = twitter_api.request('statuses/user_timeline', {'user_id': acount})
		for tweet in r:
			account_tweets.append(tweet)
	return account_tweets

# GET request for the languages in the circular area
@app.route('/languages/<string:x>/<string:y>/<string:r>', methods=['GET'])
def api_languages_circle_get(x, y, r):
    try:
        x = float(x)
        y = float(y)
        r = float(r)
    except:
        abort(400)

    results = helper_language_tweet_circle_count(x, y, r)
    return make_response(jsonify({
		'type': 'LanguagesCounted',
		'data': results
	}), 200)

# GET request for the languages in the rectangular area
@app.route('/languages/<string:sx0>/<string:sy0>/<string:sx1>/<string:sy1>', methods = ['GET'])
def api_languages_get(sx0, sy0, sx1, sy1):
	try:
		x0 = float(sx0)
		y0 = float(sy0)
		x1 = float(sx1)
		y1 = float(sy1)
	except:
		abort(400)

	results = helper_language_tweets_count(x0, y0, x1, y1)
	return make_response(jsonify({
		'type': 'LanguagesCounted',
		'data':results
	}), 200)

# GET request for the locations of all tweets and their language in the rectangular area
@app.route('/languageslocations/<string:sx0>/<string:sy0>/<string:sx1>/<string:sy1>', methods = ['GET'])
def api_languageslocations_get(sx0, sy0, sx1, sy1):
	try:
		x0 = float(sx0)
		y0 = float(sy0)
		x1 = float(sx1)
		y1 = float(sy1)
	except:
		abort(400)

	results = helper_language_tweet_locations(x0, y0, x1, y1)
	return make_response(jsonify({
		'type': 'FeatureCollection',
		'features': results
	}), 200)

# GET request for the first word_count meaningful words and their language in the rectangular area
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

# GET request for details about a place
@app.route('/place/<string:place>/<string:latitude>/<string:longitude>', methods = ['GET'])
def api_place(place, latitude, longitude):
	try:
		longitude = float(longitude)
		latitude = float(latitude)
	except:
		abort(400)

	max_distance_from_place_km = 100
	tweets_request = twitter_api.request('search/tweets', { 'q': place })
	tweets = []
	images = []
	sentiments = []
	positive_sentiments = 0
	negative_sentiments = 0
	(account_id, account_name) = helper_place_account(place)

	for tweet in tweets_request:
		images = images + helper_tweet_images(tweet)
		tweet_location = helper_tweet_geolocation(tweet)
		tweet_account_id = helper_tweet_account_id(tweet)

		tweet_distance = None
		if tweet_location is not None:
			(tweet_latitude, tweet_longitude) = tweet_location
			tweet_distance = helper_distance_km(tweet_latitude, tweet_longitude, latitude, longitude)

		tweet_sentiment = None
		if tweet['lang'] in ['en', 'fr', 'it', 'de', 'ru', 'es', 'pt'] and (tweet_distance is None or tweet_distance <= max_distance_from_place_km) and (tweet_account_id is None or account_id is None or tweet_account_id != account_id):
			tweet_sentiment = helper_tweet_sentiments(tweet)

		if tweet_sentiment is not None:
			if tweet_sentiment > 0.0:
				positive_sentiments += 1
			elif tweet_sentiment < 0.0:
				negative_sentiments += 1
			sentiments.append(tweet_sentiment)

		tweets.append((tweet_location, tweet_account_id, tweet_distance, tweet_sentiment))

	account_tweets = helper_place_account_tweets(account_id)
	for tweet in account_tweets:
		images = images + helper_tweet_images(tweet)

	count_sentiments = len(sentiments)
	average_sentiment = None
	if count_sentiments > 0:
		average_sentiment = sum(map(lambda s: (s + 1.0) * 5.0, sentiments)) / count_sentiments

	return make_response(jsonify({
		'images': list(set(images)),
		'account_id': account_id,
		'account_name': account_name,
		'average_sentiment': average_sentiment,
		'positive_sentiments': positive_sentiments,
		'negative_sentiments': negative_sentiments,
		'tweets': tweets
	}), 200)

# GET request for the HTML template
@app.route('/')
def homepage_get():
	return render_template("map.html")

# Handler for 400 (bad request) errors
@app.errorhandler(400)
def error_not_found(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

# Handler for 404 (not found) errors
@app.errorhandler(404)
def error_not_found(error):
	return make_response(jsonify({'error': 'Resource not found'}), 404)

if __name__ == '__main__':
	app.run(debug = True)
