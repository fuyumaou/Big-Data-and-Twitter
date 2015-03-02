#!env/bin/python
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'va_%r-jZ%Yl=3t9Q8ml[.Wu0!mT$Gy[gsgr/:>M8rm-]0fq`^<TK2L*x"M"\dQW'
socketio = SocketIO(app)

@app.route('/')
def view_index():
    return 'Hello world!'

if __name__ == '__main__':
    socketio.run(app)