
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
import urllib3.request
import urllib3.parse

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

GNAVI_API_KEY = os.getenv('GNAVI_API_KEY')
# BOT_SERVER_URL = os.getenv('BOT_SERVER_URL')
# os.environ['http_proxy'] = os.getenv('FIXIE_URL')
# os.environ['https_proxy'] = os.getenv('FIXIE_URL')

if GNAVI_API_KEY is None:
    print('Specify GNAVI_API_KEY as environment variable.')
    sys.exit(1)
if YOUR_CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if YOUR_CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
# if BOT_SERVER_URL is None:
#     print('Specify BOT_SERVER_URL as environment variable.')
#     sys.exit(1)
# if os.getenv('FIXIE_URL') is None:
#     print('Specify FIXIE_URL as environment variable.')
#     sys.exit(1)

# instantiation
# TODO: インスタンス生成はグローバルでなくファクトリメソッドに移したい
# TODO: グローバルに参照可能な api_callerを作成するか, 個々に作成するかどちらが良いか確認
app = Flask(__name__)
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

RESTSEARCH_URL = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
DEF_ERR_MESSAGE = """
申し訳ありません、データを取得できませんでした。
少し時間を空けて、もう一度試してみてください。
"""
NO_HIT_ERR_MESSAGE = "お近くにぐるなびに登録されている喫茶店はないようです" + chr(0x100017)
LINK_TEXT = "ぐるなびで見る"
FOLLOWED_RESPONSE = "フォローありがとうございます。位置情報を送っていただくことで、お近くの喫茶店をお伝えします" + chr(0x100059)



def call_restsearch(latitude, longitude):
    query = {
        "keyid": GNAVI_API_KEY,
        "latitude": latitude,
        "longitude": longitude,
        # TODO: category_sを動的に生成
        "category_s": "RSFST18008,RSFST18009,RSFST18010,RSFST18011,RSFST18012"
        # TODO: hit_per_pageや offsetの変更に対応 (e.g., 指定可能にする, 多すぎるときは普通にブラウザに飛ばす, など)
        # TODO: rangeをユーザーアクションによって選択可能にしたい
        # "range": search_range
    }
    params = urllib3.parse.urlencode(query, safe=",")
    response = urllib3.request.urlopen(RESTSEARCH_URL + "?" + params).read()
    result = json.loads(response)

    if "error" in result:
        if "message" in result:
            raise Exception("{}".format(result["message"]))
        else:
            raise Exception(DEF_ERR_MESSAGE)

    total_hit_count = result.get("total_hit_count", 0)
    if total_hit_count < 1:
        raise Exception(NO_HIT_ERR_MESSAGE)

    return result


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

    # signature = request.headers['X-Line-Signature']

    # body = request.get_data(as_text=True)
    # app.logger.info("Request body: "+body)

    # try:
    #     handler.handle(body, signature)
    # except InvalidSignatureError:
    #     abort(400)

    # return 'OK'


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
        
        # @handler.add(MessageEvent, message=LocationMessage)
        # def handle_location(event):
        #     if event.reply_token == "00000000000000000000000000000000":
        #         return
        #     text = event.message.address
        
        #     result = get_weather_from_location(text)
        #     line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(text=result)
        #     )


@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    if event.reply_token == "00000000000000000000000000000000":
        return

    user_lat = event.message.latitude
    user_longit = event.message.longitude

    cafe_search_result = call_restsearch(user_lat, user_longit)
    print("cafe_search_result is: {}".format(cafe_search_result))

    response_json_list = []

    # process result
    for (count, rest) in enumerate(cafe_search_result.get("rest")):
        # TODO: holiday, opentimeで表示を絞りたい
        access = rest.get("access", {})
        access_walk = "徒歩 {}分".format(access.get("walk", ""))
        holiday = "定休日: {}".format(rest.get("holiday", ""))
        image_url = rest.get("image_url", {})
        # image1 = image_url.get("shop_image1", "thumbnail_template.jpg")
        # if image1 == "":
        #     image1 = BOT_SERVER_URL + "/static/thumbnail_template.jpg"
        name = rest.get("name", "")
        opentime = "営業時間: {}".format(rest.get("opentime", ""))
        # pr = rest.get("pr", "")
        # pr_short = pr.get("pr_short", "")
        url = rest.get("url", "")

        result_text = opentime + "\n" + holiday + "\n" + access_walk + "\n"
        if len(result_text) > 60:
            result_text = result_text[:56] + "..."

        result_dict = {
            "thumbnail_image_url": "https://1.bp.blogspot.com/--R3PJRI_b-w/XvcI5TatI2I/AAAAAAABZt4/LPy_kF8BYtgYy7R76I2C2N_hVWW6Bw2dwCNcBGAsYHQ/s1600/osyougatsu_text_2021.png",
            "title": name,
            # "text": pr_short + "\n" + opentime + "\n" + holiday + "\n"
            # + access_walk + "\n",
            "text": result_text,
            "actions": {
                "label": "ぐるなびで見る",
                "uri": url
            }
        }
        response_json_list.append(result_dict)
    print("response_json_list is: {}".format(response_json_list))
    columns = [
        CarouselColumn(
            thumbnail_image_url=column["thumbnail_image_url"],
            title=column["title"],
            text=column["text"],
            actions=[
                URITemplateAction(
                    label=column["actions"]["label"],
                    uri=column["actions"]["uri"],
                )
            ]
        )
        for column in response_json_list
    ]
    # TODO: GoogleMapへのリンク実装

    messages = TemplateSendMessage(
        alt_text="喫茶店の情報をお伝えしました",
        template=CarouselTemplate(columns=columns),
    )
    print("messages is: {}".format(messages))

    line_bot_api.reply_message(
        event.reply_token,
        messages=messages
    )

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=FOLLOWED_RESPONSE)
    )


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)



