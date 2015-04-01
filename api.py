#!env/bin/python
from flask import Flask, make_response, jsonify, abort, request, url_for, render_template, session, redirect
import unirest
app = Flask(__name__)

#Mock Database --- to be replaced with actual DB
db = [
	 {'id':1,'language':'en','x':1,'y':1},
	 {'id':2,'language':'en','x':2,'y':2},
	 {'id':3,'language':'rs','x':3,'y':0}
	]
	
#List of languages to be queried on
# !! --- Update it to contain all languages in one way or another OR Sort the DB on languages OR implement any other solution for the helper
languages = ['en']

#----------------------------------------------------------------------------

# helper_languages_get 
# !! --- need to be changed to work with an actual MongoDB database
# Input: x0, y0, x1, y1 --- 4 coordinates
# Output: A List of Records of type {language, number} where number is the number
#		of tweets in the respective language
def helper_languages_get(x0,y0,x1,y1):
	results=[]
	for lang in languages:
		number_tweets_in_lang=len(filter(lambda p: (p['language']==lang and p['x']>=x0 and p['x']<=x1 and p['y']>=y0 and p['y']<=y1), db))
		if len>0:
			results.append({'language':lang,'number':number_tweets_in_lang})
	return results

#----------------------------------------------------------------------------

#----------------------------------------------------------------------------

# GET request for the languages in the area x0, y0, x1, y1
@app.route('/languages/<int:x0>/<int:y0>/<int:x1>/<int:y1>', methods = ['GET'])
def api_languages_get(x0,y0,x1,y1):
	results = helper_languages_get(x0,y0,x1,y1)
	return make_response(jsonify({'stats':results}), 200)

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------

# Handler for 404 errors
@app.errorhandler(404)
def error_not_found(error):
	return make_response(jsonify({'error': 'Resource not found'}), 404)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
	app.run(debug = True)