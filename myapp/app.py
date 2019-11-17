# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask import request

import requests
import json
import re

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

LINEBOT_API_EVENT ='https://trialbot-api.line.me/v1/events'
LINE_HEADERS = {
    'Content-type': 'application/json; charset=UTF-8',
    'X-Line-ChannelID':'**********', # Channel ID
    'X-Line-ChannelSecret':str(channel_secret), # Channel secre
    'X-Line-Trusted-User-With-ACL':'XXXXXXXXXXXXXXXXXXXXXXXXXX' # MID (of Channel)
}

def post_event( to, content):
    msg = {
        'to': [to],
        'toChannel': ********, # Fixed  value
        'eventType': "*****************", # Fixed value
        'content': content
    }
    r = requests.post(LINEBOT_API_EVENT, headers=LINE_HEADERS, data=json.dumps(msg))

def post_text( to, text ):
    content = {
        'contentType':1,
        'toType':1,
        'text':text,
    }
    post_event(to, content)


commands = (
    (re.compile('ラッシャー', 0), lambda x: 'テメエコノヤロウ'),
    (re.compile('ダンカン', 0), lambda x:'バカヤロコノヤロウ'),
)

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def hello():
    msgs = request.json['result']
    for msg in msgs:
        text = msg['content']['text']
        for matcher, action in commands:
            if matcher.search(text):
                response = action(text)
                break
        else:
            response = 'コマネチ'

        post_text(msg['content']['from'],response)

    return ''

if __name__ == "__main__":
    context = ('/etc/letsencrypt/archive/<hostname?>/cert1.pem', '/etc/letsencrypt/archive/<hostname?>/privkey1.pem')  # Please modify this
    app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=True, debug=True)

