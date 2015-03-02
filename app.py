from flask import Flask, render_template, request, redirect, url_for

ap == Flask(__name__)

@app.route('/')
def view_index():
    return 'Hello world!'

if __name__ == '__main__':
    app.run(debug = True)
