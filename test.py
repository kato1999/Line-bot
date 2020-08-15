
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
import os

from linebot.exceptions import LineBotApiError

import requests
from bs4 import BeautifulSoup
import re

import json
import sys

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
    
        # 位置情報からその日の天気を返す
        def get_weather_from_location(original_location):
            # 住所の中から郵便番号を抽出する
            location = re.findall('\d{3}-\d{4}', original_location)
            # 1回目のスクレイピングでは住所を検索し、候補から取ってくる
            url = "https://weather.yahoo.co.jp/weather/search/?p=" + location[0]
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            content = soup.find(class_="serch-table")
            # 2回目のスクレイピングで用いるURLを得る
            location_url = "http:" + content.find('a').get('href')
            r = requests.get(location_url)
            soup = BeautifulSoup(r.text, 'html.parser')
            content = soup.find(id='yjw_pinpoint_today').find_all('td')
            info = []
          
            for each in content[1:]:
                info.append(each.get_text().strip('\n'))
        
            # 時間
            time = info[:8]
            # 天気
            weather = info[9:17]
            # 気温
            temperature = info[18:26]
            # 上の3つの情報を合わせる
            weather_info = [(time[i], weather[i], temperature[i]) for i in range(8)]
          
            result = [('{0[0]}: {0[1]}, {0[2]}°C'.format(weather_info[i])) for i in range(8)]
            result = ('{}\nの今日の天気は\n'.format(original_location) + '\n'.join(result) + '\nです。')
    
            return result
        
            @handler.add(MessageEvent, message=LocationMessage)
            def handle_location(event):
                if event.reply_token == "00000000000000000000000000000000":
                    return
                text = event.message.address
            
                result = get_weather_from_location(text)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=result)
                )

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


