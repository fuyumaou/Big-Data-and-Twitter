#!env/bin/python
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from TwitterAPI import TwitterAPI
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'va_%r-jZ%Yl=3t9Q8ml[.Wu0!mT$Gy[gsgr/:>M8rm-]0fq`^<TK2L*x\dQW'
socketio = SocketIO(app)

twitter_access_token = '178658388-CDwtvkSOOb3ikZXaVeDBlxzHwj0wEyQ5ntTPhs5n'
twitter_access_token_secret = 'zJzQK6F00hwsG32STbITqvavbhYt5rtV6vZH69QbcKf8I'
twitter_consumer_key = 'bWMmJpHklikmU3fbKemgmr40H'
twitter_consumer_secret = 'MsAYHkqUuGi1bBWiTyiJiDdVCQ6DvYMt8ROsjJ1GFIFQCFP0Dp'
twitter_api = TwitterAPI(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)

filters = {}
twitter_stream_running = False
twitter_stream_stopped = True

def twitter_stream_stop_thread():
	global twitter_stream_running
	global twitter_stream_stopped
	twitter_stream_running = False
	while not twitter_stream_stopped:
		time.sleep(1)

def twitter_stream_thread():
	global twitter_stream_running
	global twitter_stream_stopped
	twitter_stream_stopped = False
	twitter_stream_running = True
	tracks = [f for f in filters.keys() if filters[f] > 0]
	if len(tracks) > 0:
		print('started stream filter on [' + ', '.join(tracks) + ']')
		r = twitter_api.request('statuses/filter', {'track': tracks})
		for data in r:
			if not twitter_stream_running:
				break
			if 'text' in data:
				hashtags = map(lambda t: '#' + t['text'].lower(), data['entities']['hashtags'])
				for hashtag in hashtags:
					socketio.emit('tweets_update', {
						'status': data['text'],
						'name': 'name',
						'avatar': ''
					}, room = hashtag)
					print('sent tweet on ' + hashtag)
	twitter_stream_stopped = True

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
			twitter_stream_stop_thread()
			threading.Thread(target = twitter_stream_thread).start()
		print('left room ' + hashtag)

@socketio.on('hashtag_subscribe')
def ws_hashtag_subscribe(data):
	hashtag = data['hashtag'].lower()
	join_room(hashtag)
	if not hashtag in filters:
		filters[hashtag] = 1
		twitter_stream_stop_thread()
		threading.Thread(target = twitter_stream_thread).start()
	else:
		filters[hashtag] += 1
	print('joined room ' + hashtag)

if __name__ == '__main__':
	socketio.run(app)