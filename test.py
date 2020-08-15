
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import(
    InvalidSignatureError, LineBotApiError
)
from linebot.models import(
    MessageEvent, TextMessage, TextSendMessage, LocationMessage,
    CarouselColumn, CarouselTemplate, FollowEvent,
    TemplateSendMessage, UnfollowEvent, URITemplateAction
)

from linebot.exceptions import LineBotApiError

import requests
from bs4 import BeautifulSoup
import re

import json
import sys

#スクレイピングファイルを読み込む
import scrape as sc

import urllib3.request
import os

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

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

        
    #-------------------天気-------------------
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


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


