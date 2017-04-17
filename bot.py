#!/usr/bin/python

import json
import logging
import argparse
import requests

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
parser.add_argument(
    'page_access_token',
    help='the Page\'s access token to be used in the outgoing API calls')
args = parser.parse_args()

# Configure logger
LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, filename='bot.log')
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger('raspbot')
logger.setLevel(logging.DEBUG)

# Send a message on behalf of the page
def send_message(recipient_id, message):
    message_data = {}
    message_data['message'] = {'text': message}
    message_data['recipient'] = {'id': recipient_id}

    logger.info('Sending message:')
    logger.info(str(message_data))

    url = 'https://graph.facebook.com/v2.6/me/messages'
    parms = {'access_token': args.page_access_token}
    res = requests.post(url, params=parms, json=message_data)

    logger.info('Server response: {} - {} - {}'.format(
        res.status_code,
        res.reason,
        res.text))

# Handle incoming messages and try to find the best response
def handle_message(message):
    logger.info('Received message:')
    logger.info(message)

    sender_id = message['sender']['id']
    text = ''
    if 'message' in message and 'text' in message['message']:
        text = message['message']['text']

    text_lower = text.lower()
    if 'hi' in text_lower or 'hello' in text_lower:
        send_message(sender_id, 'Hello, human!')
    else:
        send_message(sender_id, 'I don\'t understand that...')

# Webhook verification
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.mode') != 'subscribe':
        abort(403)

    if request.args.get('hub.verify_token') != args.verify_token:
        abort(403)

    return request.args.get('hub.challenge')

# Handle incoming messages
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
            handle_message(messaging)

    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0')
