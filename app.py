
import sys
import pymongo
import os
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,TemplateSendMessage,ButtonsTemplate,PostbackTemplateAction
)

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.environ['linetoken'])
# Channel Secret
handler = WebhookHandler(os.environ['linechannel'])


### Create seed data

SEED_DATA = [
    {
        'decade': '1970s',
        'artist': 'Debby Boone',
        'song': 'You Light Up My Life',
        'weeksAtOne': 10
    },
    {
        'decade': '1980s',
        'artist': 'Olivia Newton-John',
        'song': 'Physical',
        'weeksAtOne': 10
    },
    {
        'decade': '1990s',
        'artist': 'Mariah Carey',
        'song': 'One Sweet Day',
        'weeksAtOne': 16
    }
]

### Standard URI format: mongodb://[dbuser:dbpassword@]host:port/dbname

uri = 'mongodb://heroku_g4mqlp4n:b2fuh42r8dvlnaofkcrv97sv93@ds225010.mlab.com:25010/heroku_g4mqlp4n' 
client = pymongo.MongoClient(uri)
db = client.get_default_database()


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    message = TextSendMessage(text='echo : ' + event.message.text)
    
    if('搜尋' in event.message.text) or ('查詢' in event.message.text):
        pass
    replay_message(event,message)
    save_message(event)

def replay_message(event,message):
    line_bot_api.reply_message(
        event.reply_token,message)
        
def push_message(event,message):
    line_bot_api.push_message(
        event.source.user_id,
        message)     

def save_message(event):
    data = {
        'decade': '1990s',
        'artist': 'Mariah Carey',
        'song': 'One Sweet Day',
        'weeksAtOne': 16,
        'id': event.message.id,
        'type': event.message.type,
        'text' : event.message.text
    },
    message_collection = db['message'] # collection; it is created automatically when we insert.
    message_collection.insert_many(data) # Note that the insert method can take either an array or a single dict.
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
