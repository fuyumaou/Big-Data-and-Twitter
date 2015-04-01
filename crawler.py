import re
import langid
from TwitterAPI import TwitterAPI

twitter_access_token = '178658388-CDwtvkSOOb3ikZXaVeDBlxzHwj0wEyQ5ntTPhs5n'
twitter_access_token_secret = 'zJzQK6F00hwsG32STbITqvavbhYt5rtV6vZH69QbcKf8I'
twitter_consumer_key = 'bWMmJpHklikmU3fbKemgmr40H'
twitter_consumer_secret = 'MsAYHkqUuGi1bBWiTyiJiDdVCQ6DvYMt8ROsjJ1GFIFQCFP0Dp'

def tweet_text_language(tweet_text):
	(language, confidence) = langid.classify(tweet_text)
	if confi
	return language

def tweet_text_process(tweet_text):
	tweet_text = re.sub(r'[^\x00-\x7F]+',' ', tweet_text)
	tweet_words = re.split('\s', tweet_text) # split text into words
	tweet_words = map(lambda w: re.sub('\#.*', '', w), tweet_words) # remove hashtags
	tweet_words = map(lambda w: re.sub('\@.*', '', w), tweet_words) # remove user mentions
	tweet_words = map(lambda w: re.sub('^.*http.*', '', w), tweet_words) # remove links
	tweet_words = filter(lambda w: w != '', tweet_words) # filter empty words
	return ' '.join(tweet_words) # join words by a space


if __name__ == '__main__':
	twitter_api = TwitterAPI(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)
	twitter_stream = twitter_api.request('statuses/filter', {'locations': '-14.02,49.67,2.09,61.06'}) # get tweets stream for UK
	for tweet in twitter_stream:
		if 'text' in tweet:
			tweet_text = tweet_text_process(data['text'])
			tweet_language = get_langid(tweet_text)
			if tweet_language != 'en':
				print tweet_text
				print tweet_language

