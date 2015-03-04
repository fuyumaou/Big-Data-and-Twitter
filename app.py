#!env/bin/python
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from twython import TwythonStreamer
import gevent
from gevent import monkey

monkey.patch_all()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'va_%r-jZ%Yl=3t9Q8ml[.Wu0!mT$Gy[gsgr/:>M8rm-]0fq`^<TK2L*x\dQW'
socketio = SocketIO(app)

twitter_access_token = '178658388-CDwtvkSOOb3ikZXaVeDBlxzHwj0wEyQ5ntTPhs5n'
twitter_access_token_secret = 'zJzQK6F00hwsG32STbITqvavbhYt5rtV6vZH69QbcKf8I'
twitter_consumer_key = 'bWMmJpHklikmU3fbKemgmr40H'
twitter_consumer_secret = 'MsAYHkqUuGi1bBWiTyiJiDdVCQ6DvYMt8ROsjJ1GFIFQCFP0Dp'

class TwitterStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
			hashtags = map(lambda t: '#' + t['text'].lower(), data['entities']['hashtags'])
			for hashtag in hashtags:
				socketio.emit('tweets_update', {
					'status': data['text'],
					'name': 'name',
					'avatar': ''
				}, room = hashtag)
				print('sent tweet on ' + hashtag)
    def on_error(self, status_code, data):
        print status_code


filters = {}
twitter_stream = TwitterStreamer(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)

def twitter_stream_thread():
	tracks = [f for f in filters.keys() if filters[f] > 0]
	if len(tracks) > 0:
		print('started stream filter on [' + ', '.join(tracks) + ']')
		twitter_stream.statuses.filter(track = tracks)

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
			twitter_stream.disconnect()
			gevent.spawn(twitter_stream_thread)
		print('left room ' + hashtag)

@socketio.on('hashtag_subscribe')
def ws_hashtag_subscribe(data):
	hashtag = data['hashtag'].lower()
	join_room(hashtag)
	if not hashtag in filters:
		filters[hashtag] = 1
		twitter_stream.disconnect()
		gevent.spawn(twitter_stream_thread)
	else:
		filters[hashtag] += 1
	print('joined room ' + hashtag)

if __name__ == '__main__':
	gevent.spawn(socketio.run, app).join()