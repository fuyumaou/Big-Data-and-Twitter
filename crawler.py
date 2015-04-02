import re
import os
from TwitterAPI import TwitterAPI
from pymongo import MongoClient

twitter_access_token = '178658388-CDwtvkSOOb3ikZXaVeDBlxzHwj0wEyQ5ntTPhs5n'
twitter_access_token_secret = 'zJzQK6F00hwsG32STbITqvavbhYt5rtV6vZH69QbcKf8I'
twitter_consumer_key = 'bWMmJpHklikmU3fbKemgmr40H'
twitter_consumer_secret = 'MsAYHkqUuGi1bBWiTyiJiDdVCQ6DvYMt8ROsjJ1GFIFQCFP0Dp'

def tweet_text_words(tweet_text):
	tweet_text = re.sub(r'[^\x00-\x7F]+',' ', tweet_text)
	tweet_words = re.split('\s', tweet_text) # split text into words
	tweet_words = map(lambda w: re.sub('\#.*', '', w), tweet_words) # remove hashtags
	tweet_words = map(lambda w: re.sub('\@.*', '', w), tweet_words) # remove user mentions
	tweet_words = map(lambda w: re.sub('^.*http.*', '', w), tweet_words) # remove links
	tweet_words = filter(lambda w: w != '', tweet_words) # filter empty words
	return tweet_words

def tweet_process(tweet, stopwords, mongo_db):
	tweet_text_dirty = tweet['text']
	tweet_words = tweet_text_words(tweet_text_dirty)
	tweet_text = ' '.join(tweet_words)
	tweet_non_stopwords = filter(lambda w: w not in stopwords, tweet_words)

	mongo_db_languages = mongo_db['languages']

	tweet_language = tweet['lang']
	if tweet_language != 'und':
		mongo_db_languages.update({
			'language': tweet_language
		}, {
			'$push': {
				'tweets': tweet_text
			}
		}, True)

	print(tweet_text, tweet_language, tweet_non_stopwords)

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
	twitter_stream = twitter_api.request('statuses/filter', {'locations': '-14.02,49.67,2.09,61.06'}) # get tweets stream for UK
	for tweet in twitter_stream:
		if 'text' in tweet:
			tweet_process(tweet, stopwords, mongo_db)
