#!/usr/bin/python

import argparse

from flask import Flask
from flask import abort
from flask import request

# Init Flask
app = Flask(__name__)

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    'verify_token',
    help='token that Facebook will pass to the webhook for verification')
args = parser.parse_args()

# Webhook verification
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.mode') != 'subscribe':
        abort(403)

    if request.args.get('hub.verify_token') != args.verify_token:
        abort(403)

    return request.args.get('hub.challenge')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
