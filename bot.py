#!/usr/bin/python

import sys
import json
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

@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)

    # Make sure this is a page subscription
    if data['object'] != 'page':
        abort(400)

    # Iterate over each entry - there may be multiple if batched
    for entry in data['entry']:
        for messaging in entry['messaging']:
            if 'message' not in messaging:
                continue
            sys.stderr.write('Received message:\n')
            sys.stderr.write(str(messaging) + '\n')

    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0')
