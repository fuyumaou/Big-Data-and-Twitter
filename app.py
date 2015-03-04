#!env/bin/python
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from logentries import LogentriesHandler
import logging


app = Flask(__name__)
app.config['SECRET_KEY'] = 'va_%r-jZ%Yl=3t9Q8ml[.Wu0!mT$Gy[gsgr/:>M8rm-]0fq`^<TK2L*x\dQW'
log = logging.getLogger('logentries')
app.logger.addHandler('10fe5f8f-ff8b-4169-8eb8-cd1262727b04')
app.logger.setLevel(logging.INFO)
socketio = SocketIO(app)

class TwitterListener(StreamListener):
	def on_status(self, status):
		hashtags = map(lambda t: '#' + t['text'].lower(), status.entities['hashtags'])
		for hashtag in hashtags:
			socketio.emit('tweets_update', {
				'status': status.text,
				'name': 'name',
				'avatar': ''
			}, room = hashtag)
			app.logger.info('sent tweet on ' + hashtag)
		return True
	def on_error(self, status):
		print status

twitter_access_token = '178658388-CDwtvkSOOb3ikZXaVeDBlxzHwj0wEyQ5ntTPhs5n'
twitter_access_token_secret = 'zJzQK6F00hwsG32STbITqvavbhYt5rtV6vZH69QbcKf8I'
twitter_consumer_key = 'bWMmJpHklikmU3fbKemgmr40H'
twitter_consumer_secret = 'MsAYHkqUuGi1bBWiTyiJiDdVCQ6DvYMt8ROsjJ1GFIFQCFP0Dp'

twitter_listener = TwitterListener()
twitter_auth = OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
twitter_auth.set_access_token(twitter_access_token, twitter_access_token_secret)
twitter_stream = Stream(twitter_auth, twitter_listener)

filters = {}

def restart_stream():
	twitter_stream.disconnect()
	tracks = [filter for filter in filters.keys()]
	app.logger.info('started stream filter on [' + ', '.join(tracks) + ']')
	twitter_stream.filter(track = tracks, async = True)

@app.route('/')
def view_index():
	return render_template('feed.html')

@socketio.on('hashtag_unsubscribe')
def ws_hashtag_unsubscribe(data):
	hashtag = data['hashtag'].lower()
	if hashtag != '':
		leave_room(hashtag)
		filters[hashtag] -= 1
		if filters[hashtag] == 0:
			filters.pop(hashtag, None)
			restart_stream()
		app.logger.info('left room ' + hashtag)

@socketio.on('hashtag_subscribe')
def ws_hashtag_subscribe(data):
	hashtag = data['hashtag'].lower()
	if not hashtag in filters:
		filters[hashtag] = 1
		restart_stream()
	else:
		filters[hashtag] += 1
	join_room(hashtag)
	app.logger.info('joined room ' + hashtag)

if __name__ == '__main__':
	socketio.run(app)