import re
import os
from TwitterAPI import TwitterAPI
from pymongo import MongoClient, GEOSPHERE
import datetime

twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
twitter_access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
twitter_consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
twitter_consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')

def tweet_text_words(tweet_text):
	tweet_text = re.sub(r'[^\x00-\x7F]+',' ', tweet_text) # remove non-printable characters
	tweet_words = re.split('\s', tweet_text) # split text into words
	tweet_words = map(lambda w: re.sub('\#.*', '', w), tweet_words) # remove hashtags
	tweet_words = map(lambda w: re.sub('\@.*', '', w), tweet_words) # remove user mentions
	tweet_words = map(lambda w: re.sub('^.*http.*', '', w), tweet_words) # remove links
	tweet_words = filter(lambda w: w != '', tweet_words) # filter empty words
	return tweet_words

def tweet_get_geolocation(tweet):
	if 'coordinates' in tweet:
		geo = tweet['coordinates']
		if geo is not None and 'type' in geo and geo['type'] == 'Point' and 'coordinates' in geo:
			coordinates = geo['coordinates']
			return {
				'latitude': coordinates[1],
				'longitude': coordinates[0]
			}
		return None
	else:
		return None

def tweet_process(tweet, stopwords, mongo_db):
	tweet_text_dirty = tweet['text']
	tweet_words = tweet_text_words(tweet_text_dirty)
	tweet_text = ' '.join(tweet_words)
	tweet_words_filtered = filter(lambda w: len(w) > 3 and w not in stopwords and w.isalnum(), map(lambda w: w.lower(), tweet_words))
	tweet_geolocation = tweet_get_geolocation(tweet)
	tweet_language = tweet['lang']

	mongo_db_languages = mongo_db['languages0']
	if tweet_language != 'und' and tweet_geolocation is not None:
		mongo_db_languages.insert({
			'language': tweet_language,
			'location': [
				tweet_geolocation['longitude'],
				tweet_geolocation['latitude']
			],
			"time": datetime.datetime.utcnow()
		})

	mongo_db_words = mongo_db['words0']
	if tweet_language != 'und' and tweet_geolocation is not None:
		for word in tweet_words_filtered:
			mongo_db_words.insert({
				'word': word,
				'location': [
					tweet_geolocation['longitude'],
					tweet_geolocation['latitude']
				],
				"time": datetime.datetime.utcnow()
			})

	print(tweet_text, tweet_geolocation, tweet_language, tweet_words_filtered)

def read_stopwords():
	stopwords_file = open('stopwords')
	lines = stopwords_file.readlines()
	return [line.strip() for line in lines]

def read_countries():
	countries_file = open('countries')
	lines = countries_file.readlines()
	countries = {}
	for line in lines:
		words = line.rstrip().split(' ')
		countries[words[0]] = ','.join(words[1:])
	return countries

if __name__ == '__main__':
	mongo_url = os.getenv('MONGOLAB_URI')
	mongo_client = MongoClient(mongo_url)
	mongo_db = mongo_client.get_default_database()
	stopwords = read_stopwords()
	twitter_api = TwitterAPI(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)
	countries = read_countries()
	twitter_stream = twitter_api.request('statuses/filter', {'locations': countries['France'] })
	for tweet in twitter_stream:
		if 'text' in tweet:
			tweet_process(tweet, stopwords, mongo_db)
