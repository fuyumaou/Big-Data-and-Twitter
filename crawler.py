import re
import os
from TwitterAPI import TwitterAPI
from pymongo import MongoClient

twitter_access_token = '178658388-CDwtvkSOOb3ikZXaVeDBlxzHwj0wEyQ5ntTPhs5n'
twitter_access_token_secret = 'zJzQK6F00hwsG32STbITqvavbhYt5rtV6vZH69QbcKf8I'
twitter_consumer_key = 'bWMmJpHklikmU3fbKemgmr40H'
twitter_consumer_secret = 'MsAYHkqUuGi1bBWiTyiJiDdVCQ6DvYMt8ROsjJ1GFIFQCFP0Dp'

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
	tweet_words_filtered = filter(lambda w: len(w) > 3 and w not in stopwords, map(lambda w: w.lower(), tweet_words))
	tweet_geolocation = tweet_get_geolocation(tweet)
	tweet_language = tweet['lang']
	print(tweet_language);print(tweet_text_dirty);print('\n');

	mongo_db_languages = mongo_db['languages']
	if tweet_language != 'und' and tweet_geolocation is not None:
		mongo_db_languages.update({
			'language': tweet_language
		}, {
			'$push': {
				'tweet': tweet_geolocation
			}
		}, True)

	mongo_db_words = mongo_db['words']
	if tweet_language == 'en' and tweet_geolocation is not None:
		for word in tweet_words_filtered:
			word_clean = filter(lambda c: c.isalnum(), word)
			mongo_db_words.update({
				'word': word_clean
			}, {
				'$push': {
					'tweet': tweet_geolocation
				}
			}, True)

	#print(tweet_text, tweet_geolocation, tweet_language, tweet_words_filtered)

def read_stopwords():
	stopwords_file = open('stopwords')
	lines = stopwords_file.readlines()
	return [line.strip() for line in lines]


if __name__ == '__main__':
	mongo_url = os.getenv('MONGOLAB_URI')
	mongo_client = MongoClient(mongo_url)
	mongo_db = mongo_client.get_default_database()
	stopwords = read_stopwords()
	twitter_api = TwitterAPI(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)
	# Old UK coords: -14.02,49.67,2.09,61.06
	twitter_stream = twitter_api.request('statuses/filter', {'locations': '5.955,45.818,10.507,47.810'})# get tweets stream for Switzerland
	for tweet in twitter_stream:
		if 'text' in tweet:
			tweet_process(tweet, stopwords, mongo_db)
