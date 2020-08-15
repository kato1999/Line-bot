
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import(
    InvalidSignatureError
)
from linebot.models import(
    MessageEvent, TextMessage, TextSendMessage
)
import os

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["E5RAfEWtDO+YAN/E2jKiOQbYXH7mBM/QMJC5zELdL6fNdnvpQthZVIgh6a+4HtReiw0UmVnPJvHQDxsbjlqQ4OduF9S09JMPlU26PDIaha+rF1Uk1g7EJ8YZ+HvjfHpwK1xVkRiLb4IeguFDM3tqaAdB04t89/1O/w1cDnyilFU="]
YOUR_CHANNEL_SECRET = os.environ["583c20b8d3942a548ca5205d49b4606a"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: "+body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

