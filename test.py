from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import(
    InvalidSignatureError
)
from linebot.models import *
import os

from linebot.exceptions import LineBotApiError

import requests
from bs4 import BeautifulSoup
import re

import json
import sys
import urllib3.request

import scrape as sc

from carousel import create_carousel, rest_search

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

if YOUR_CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if YOUR_CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except LineBotApiError as e:
        app.logger.exception(f'LineBotApiError: {e.status_code} {e.message}', e)
        raise e

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
        
    text = event.message.text

    if 'カフェ' in text:

        line_bot_api.reply_message(
            event.reply_token,
            [
            TextSendMessage(text='位置情報を教えてください。'),
            TextSendMessage(text='line://nv/location')
            ]
        )

        @handler.add(MessageEvent, message=LocationMessage)
        def handle_location(event):
            lat = event.message.latitude
            lon = event.message.longitude

            rest_datas = rest_search(lat, lon)
        
            if rest_datas:
                template_message = TemplateSendMessage(alt_text='周辺のカフェだよ!', template=create_carousel(rest_datas))
                line_bot_api.reply_message(
                    event.reply_token,
                    template_message
                    )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                    TextSendMessage(text='近くにお店がありません。'),
                    ]
                )    


    elif '天気' in text:
        line_bot_api.reply_message(
            event.reply_token,
            [
            TextSendMessage(text='位置情報を教えてください。'),
            TextSendMessage(text='line://nv/location')
            ]
        )

        @handler.add(MessageEvent, message=LocationMessage)
        def handle_location(event):
            if event.reply_token == "00000000000000000000000000000000":
                return
            text = event.message.address
        
            result = sc.get_weather_from_location(text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result)
            )
    
    else:
        line_bot_api.reply_message(
            event.reply_token,
            [
            TextSendMessage(text='「カフェ」で近くのカフェ情報がわかります！\n「天気」で天気情報がわかります！')
            ]
        )

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

