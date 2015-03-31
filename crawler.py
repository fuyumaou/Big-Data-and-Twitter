import os
import unirest
from TwitterAPI import TwitterAPI

twitter_access_token = '178658388-CDwtvkSOOb3ikZXaVeDBlxzHwj0wEyQ5ntTPhs5n'
twitter_access_token_secret = 'zJzQK6F00hwsG32STbITqvavbhYt5rtV6vZH69QbcKf8I'
twitter_consumer_key = 'bWMmJpHklikmU3fbKemgmr40H'
twitter_consumer_secret = 'MsAYHkqUuGi1bBWiTyiJiDdVCQ6DvYMt8ROsjJ1GFIFQCFP0Dp'
twitter_api = TwitterAPI(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)


def get_language(text):
	print text
	languages = []
	try:
		response = unirest.post("https://community-language-detection.p.mashape.com/detect?key=d4e704793e7ffe2ea223bdd874639c3f",
			headers = {
				"X-Mashape-Key": "BCpWshjnCVmshxRysoCdECpHdKrMp1LgcscjsnV0MJ3SBq1dq0",
				"Content-Type": "application/x-www-form-urlencoded",
				"Accept": "application/json"
			},
			params = {
				"q": text
			}
		)
		response = response.body
		for detection in response['data']['detections']:
			if detection['isReliable'] == True:
				languages.append(detection['language'])
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		pass
	return languages


if __name__ == '__main__':
	r = twitter_api.request('statuses/filter', {'locations': '-14.02,49.67,2.09,61.06'})
	for data in r:
		if 'text' in data:
			tweet_text = data['text']
			tweet_languages = get_language(tweet_text)
			if tweet_languages:
				for language in tweet_languages:
					print language