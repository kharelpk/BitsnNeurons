from flask import Flask, request, jsonify, redirect, session, url_for, send_from_directory
from authlib.integrations.flask_client import OAuth
import os
import json
from waitress import serve
import random
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']


# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ['CLIENT_ID'],  # Replace with your client ID
    client_secret=os.
    environ['CLIENT_SECRET'],  # Replace with your client secret
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v2/userinfo',
    client_kwargs={'scope': 'email'},
)


# API endpoint to test that the app is working
@app.route('/test', methods=['GET'])
def test_api():
  return jsonify({"message": "API is working!"})


# API endpoint to test that authentication worked
@app.route('/hello', methods=['GET'])
def hello():
  # Return the email of the account who logged in
  user_email = session.get('email', 'No user logged in')
  return jsonify({"message": f"Your email is {user_email}"})

@app.route('/login')
def login():
  redirect_uri = url_for('authorize', _external=True)
  print("Redirect URI:", redirect_uri)
  return google.authorize_redirect(redirect_uri=redirect_uri)

@app.route('/authorize')
def authorize():
  try:
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    return redirect(url_for('hello'))
  except Exception as e:
    app.logger.error(f"Error in /authorize: {e}")
    return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
  #app.run(debug=True)
  serve(app, host='0.0.0.0', port="8080")
