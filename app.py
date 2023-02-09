from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from dotenv import dotenv_values
import lineFunc

config = dotenv_values('.env')

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(config['LINEBOTAPI'])
# Channel Secret
handler = WebhookHandler(config['WEBHOOK'])

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    # 數位簽章
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

status = 1

# 處理訊息
# event.message.text 用來獲取使用者輸入的訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global status
    enter = event.message.text
    reply = ''
    message=''
    if status == 2:
        data = lineFunc.getAQI()
        msg = data.get(enter, '找不到地區')
        message = TextSendMessage(text=msg)
        status = 1
    else:
        if '空氣' in enter:
            message = TextSendMessage(text='請輸入地區')
            status = 2
        elif '利率' in enter:
            reply=lineFunc.getRate()
            message = TextSendMessage(text=reply)
        elif '紫棋' in enter:
            reply=lineFunc.getImg()
            message = ImageSendMessage(original_content_url=reply, preview_image_url=reply)
        elif '電視' in enter:
            reply = lineFunc.getTV()
            message = TextSendMessage(text=reply)
        else:
            reply = enter
            message = TextSendMessage(text=reply)
    
    line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    
    latitude = event.message.latitude
    longitude = event.message.longitude
    
    reply = lineFunc.getAQIByLocation(latitude, longitude)
    
    message = TextSendMessage(text=reply)
    
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
