#!flask/bin/python
import os
import logging
from pathlib import Path

from flask import Flask, render_template, redirect, url_for, request, jsonify
from stravalib import Client
from dotenv import load_dotenv

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/")
def login():
    c = app.config['global_client']
    url = c.authorization_url(client_id=os.environ['STRAVA_CLIENT_ID'],
                              redirect_uri=url_for('.logged_in', _external=True),
                              approval_prompt='auto',
                              scope='activity:write')
    return render_template('login.html', authorize_url=url)


@app.route("/strava-oauth")
def logged_in():
    """
    Method called by Strava (redirect) that includes parameters.
    - state
    - code
    - error
    """
    error = request.args.get('error')
    state = request.args.get('state')
    if error:
        return render_template('login_error.html', error=error)
    else:
        code = request.args.get('code')
        client = app.config['global_client']
        access_token = client.exchange_code_for_token(client_id=os.environ['STRAVA_CLIENT_ID'],
                                                      client_secret=os.environ['STRAVA_CLIENT_SECRET'],
                                                      code=code)
        # Probably here you'd want to store this somewhere -- e.g. in a database.
        strava_athlete = client.get_athlete()

        return render_template('login_results.html', athlete=strava_athlete, access_token=access_token)


def start(client: Client):
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    app.config['global_client'] = client
    app.run()
