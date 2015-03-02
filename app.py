#!env/bin/python
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'va_%r-jZ%Yl=3t9Q8ml[.Wu0!mT$Gy[gsgr/:>M8rm-]0fq`^<TK2L*x\dQW'
socketio = SocketIO(app)

@app.route('/')
def view_index():
    return render_template('feed.html')

@socketio.on('search_hashtags')
def ws_search_hashtags(data):
    socketio.emit('tweets_update', data)

if __name__ == '__main__':
    socketio.run(app, host = '0.0.0.0')