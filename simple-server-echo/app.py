# -*- coding: utf-8 -*-
import os
import sys
import wsgiref.simple_server
from argparse import ArgumentParser

from builtins import bytes
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
from linebot.utils import PY3
import ssl
import MeCab
import pymysql.cursors

class CreateResponceText:
    def wakachi(self, msg_text):
        print(msg_text)
        tagger = MeCab.Tagger('-Owakati')
        mecab_result = tagger.parse(msg_text)
        wakachi_list = mecab_result.split(' ')
        return wakachi_list

    def return_on(self, wakachi_list):
        reply_on = False
        name_list = {'スター', 'star', 'スタ'}
        for word in wakachi_list:
            if word in name_list:
                reply_on = True
        return reply_on 

    def return_text(self, wakachi_list):
        save_list = {'メモ', '記録', '保存', 'セーブ'}
        get_list = {'オススメ', 'おすすめ', '教えて', 'ある'}

        return_msg = ''
        for word in wakachi_list:
            if word in save_list:
                return_msg = '何をメモすれば良い？'
            if word in get_list:
                return_msg = 'オススメはこれだよ'
        return return_msg

    #def quickstart(self, meg_text):
    #    save_list = {'メモ', '記録', '保存', 'セーブ'}
    #    if save_list in wakachi_list
    #    return True

class MessageDatabase:
    def __init__(self):
        self.connection = pymysql.connect(host='localhost',
                                         user='pyuser',
                                         password='pypasswd',
                                         db='pydb',
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)


    def save_message(self, msg_text):
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `comments` (`comment`, `user`) VALUES (%s, %s)"
                cursor.execute(sql, (msg_text, 'kotaro'))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

        finally:
            self.connection.close()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
channel_secret='*****************'  # Please modify this
channel_access_token='****************************************************************************'  # Please modify this

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

class current_situation:
    called_name = False
    get_storage = False
    #def return_called_name(self):
    #    return called_name
    #def return_get_storage(self):
    #    return get_storage
    #def set_called_name(self, truefalse):
    #    called_name = truefalse
    #def set_get_storage(self, truefalse):
    #    get_storage = truefalse

def application(environ, start_response):
    crt = CreateResponceText()
    cs = current_situation
    md = MessageDatabase()
    print('Z')
    # check request path
    if environ['PATH_INFO'] != '/callback':
        start_response('404 Not Found', [])
        print('responced "404 Not Found"')
        return create_body('Not Found')

    print('A')
    # check request method
    if environ['REQUEST_METHOD'] != 'POST':
        start_response('405 Method Not Allowed', [])
        print('responced "405 Method Not Allowed"')
        return create_body('Method Not Allowed')

    print('B')
    # get X-Line-Signature header value
    signature = environ['HTTP_X_LINE_SIGNATURE']

    print('C')
    # get request body as text
    wsgi_input = environ['wsgi.input']
    content_length = int(environ['CONTENT_LENGTH'])
    body = wsgi_input.read(content_length).decode('utf-8')

    print('D')
    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        start_response('400 Bad Request', [])
        return create_body('Bad Request')

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        wakachi_list = crt.wakachi(event.message.text)
        if 'メモ' in event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='何をメモすれば良い？')
            )
            cs.get_storage = True
            cs.called_name = False

        elif crt.return_on(wakachi_list) and not cs.get_storage: #今回、呼ばれた
            return_msg = '呼んだ？'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=return_msg)
            )
            cs.called_name = True

        else: #今回、呼ばれてない
            if cs.called_name: #前回、呼ばれた
                return_msg = crt.return_text(wakachi_list)
                if return_msg == '': #今回、命令わからず
                    return_msg = event.message.text #オウム返しするだけ 
                else: #今回、命令を受け取った
                    cs.get_storage = True

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=return_msg)
                )
                cs.called_name = False

            elif cs.get_storage: #前回、メモしろと言われた
                md.save_message(event.message.text)

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='メモしたよ〜!')
                )
                cs.get_storage = False

    start_response('200 OK', [])
    return create_body('OK')


def create_body(text):
    if PY3:
        return [bytes(text, 'utf-8')]
    else:
        return text


if __name__ == '__main__':
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=443, help='port')#443
    options = arg_parser.parse_args()

    httpd = wsgiref.simple_server.make_server('', int(options.port), application)
    httpd.socket = ssl.wrap_socket(httpd.socket,
        server_side=True,
        keyfile = "/etc/letsencrypt/archive/<hostname?>/privkey1.pem",  # Please modify this
        certfile = "/etc/letsencrypt/archive/<hostname?>/fullchain1.pem")  # Please modify this

    print("Serving on port " + str(options.port) + "...")
    httpd.serve_forever()
