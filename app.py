from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,TemplateSendMessage,ButtonsTemplate,PostbackTemplateAction,PostbackEvent,MessageTemplateAction,URITemplateAction,DatetimePickerTemplateAction
)
import os
import sys
import pymongo
import datetime


#import custom function
from linotravel_air_ticket_info  import find_air_ticket_info 

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.environ['linetoken'])
# Channel Secret
handler = WebhookHandler(os.environ['linechannel'])

### Standard URI format: mongodb://[dbuser:dbpassword@]host:port/dbname
uri = 'mongodb://heroku_g4mqlp4n:b2fuh42r8dvlnaofkcrv97sv93@ds225010.mlab.com:25010/heroku_g4mqlp4n' 
client = pymongo.MongoClient(uri)
db = client.get_default_database()

#======================parameter==================
session_dict = {}
#session_second_list = []
region_list = ["台北","TPE","首爾","SEL","ICN"]

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

@handler.add(PostbackEvent, message=None)
def handle_Postback(event):
    print("Now event in handle_Postback handle")
    user_key = event.source.user_id
    print(event)
    print(event.postback.data)
    if(event.postback.data == 'reSearch = true'):
        session_dict[user_key] = []
        session_second_list = list(session_dict[user_key])
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    user_key = event.source.user_id
    if ('重新搜尋' in event.message.text):
        session_dict[user_key] = []
        session_second_list = list(session_dict[user_key])
        session_second_list.append(event.message.text)
        session_dict[user_key] = list(session_second_list)
        message_text_tmp = "請問出發地點 ?  (例如:台北、TPE)"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message)
    elif (user_key not in session_dict) :
        if(('搜尋機票' in event.message.text) or ('查詢機票' in event.message.text)):
            session_second_list = []
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問出發地點 ?  (例如:台北、TPE)"         
        else:
            message_text_tmp = "抱歉目前僅提供搜尋機票功能，可打 搜尋機票 即可搜尋機票"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message)
    elif (len(session_dict[user_key]) == 1):
        if(event.message.text in region_list ):
            session_second_list = list(session_dict[user_key])
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問目的地 ?  (例如:首爾)"   
        else:
            message_text_tmp = "很抱歉，請輸入正確的出發地點，如機場或是國家"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message)
    elif (len(session_dict[user_key]) == 2):
        if(event.message.text in region_list ):
            session_second_list = list(session_dict[user_key])
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問出發日期? (日期格式 :2018年5月1號 請打 20180501 )"
                
        else:
            message_text_tmp = "很抱歉，請輸入正確的目的地，如機場或是國家"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message)    
    elif (len(session_dict[user_key]) == 3): 
        if(event.message.text == '20180531'):
            session_second_list = list(session_dict[user_key])
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問回國日期? (日期格式 :2018年5月1號 請打 20180501 )"    
        else:
            message_text_tmp = "很抱歉，請輸入正確的日期格式，:例如2018年5月1號 請打 20180501"
        message = TextSendMessage(text=message_text_tmp)        
        push_message(event.source.user_id,choice_datatime())
    elif (len(session_dict[user_key]) == 4): 
        if(event.message.text == '20180608'):
            session_second_list = list(session_dict[user_key])
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "搜尋中，請稍後"
            message = TextSendMessage(text=message_text_tmp)        
            replay_message(event,message)
            search_air_tickest(event)   
        else:
            message_text_tmp = "很抱歉，請輸入正確的日期格式，:例如2018年5月1號 請打 20180501"
            message = TextSendMessage(text=message_text_tmp)        
            replay_message(event,message)
    elif (user_key in session_dict) and (len(session_dict[user_key]) == 0):
        if(('搜尋機票' in event.message.text) or ('查詢機票' in event.message.text)):
            session_second_list = []
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問出發地點 ?  (例如:台北、TPE)"   
        else:
            message_text_tmp = "抱歉目前僅提供搜尋機票功能，可打 搜尋機票 即可搜尋機票"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message) 
    else:
        message = TextSendMessage(text="程式目前維護中，請見諒")        
        replay_message(event,message)


def replay_message(event,message):
    save_message(event)
    line_bot_api.reply_message(
        event.reply_token,message)
        
def push_message(user_id,message):
    line_bot_api.push_message(
        user_id,
        message)     

def save_message(event):
    data = {
        'user_id': event.source.user_id,
        'id': event.message.id,
        'type': event.message.type,
        'text' : event.message.text
    },
    message_collection = db['message'] # collection; it is created automatically when we insert.
    message_collection.insert_many(data) # Note that the insert method can take either an array or a single dict.

def choice_datatime():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    buttons_template_message = TemplateSendMessage(
        alt_text='DatetimePicker',
        template=ButtonsTemplate(
            title='選擇日期',
            text='請選擇日期',
            actions=[
                DatetimePickerTemplateAction(
                    label = "選擇出國日期",
                    mode = "datetime",
                    data="action=sell&itemid=2&mode=date",
                    initial = "2017-12-25t00:00",
                    max="2018-10-24t23:59",
                    min="2017-12-25t00:00"
                )                
            ]
        )
    )
    return buttons_template_message
def search_air_tickest(event):
    keys_list = ["Depart_tickets","Arrive_tickets"]
    tickets_keys = ['ArriveAirport','ArriveDate','DepartAirport','DepartDate','SellSeat','TotalFare']
    tickets_info = find_air_ticket_info()
    min_price = 100000
    user_id = event.source.user_id
    print("user_id is "+user_id)
    for item in tickets_info.keys():
        tickets_text = ""
        tickets_text += "====去程====\n"
        tickets_text += "出發地點:"+tickets_info[item][keys_list[0]]['TPE']['DepartAirport']+'\n'
        tickets_text += "出發時間:"+tickets_info[item][keys_list[0]]['TPE']['DepartDate']+'\n'
        tickets_text += "抵達地點:"+tickets_info[item][keys_list[0]]['TPE']['ArriveAirport']+'\n'
        tickets_text += "抵達時間:"+tickets_info[item][keys_list[0]]['TPE']['ArriveDate']+'\n'
        tickets_text += "====回程====\n"
        tickets_text += "出發地點:"+tickets_info[item][keys_list[1]]['ICN']['DepartAirport']+'\n'
        tickets_text += "出發時間:"+tickets_info[item][keys_list[1]]['ICN']['DepartDate']+'\n'
        tickets_text += "抵達地點:"+tickets_info[item][keys_list[1]]['ICN']['ArriveAirport']+'\n'
        tickets_text += "抵達時間:"+tickets_info[item][keys_list[1]]['ICN']['ArriveDate']+'\n'
        tickets_text += "====票價====\n"
        tickets_text += "每人含稅價格: NT"+str(tickets_info[item][keys_list[1]]['ICN']['TotalFare'])+'\n'
        if(min_price > tickets_info[item][keys_list[1]]['ICN']['TotalFare']):
            min_price = tickets_info[item][keys_list[1]]['ICN']['TotalFare']
            push_tickets_info = TextSendMessage(text=tickets_text)
            push_message(user_id,push_tickets_info) 
    buttons_template_message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://example.com/image.jpg',
            title='Menu',
            text='是否重新搜尋新航班',
            actions=[
                PostbackTemplateAction(
                    label='重新搜尋',
                    text='重新搜尋新航班',
                    data='reSearch = true'
                ),
                MessageTemplateAction(
                    label='message',
                    text='message text'
                ),
                URITemplateAction(
                    label='uri',
                    uri='http://example.com/'
                )
            ]
        )
    )
    push_message(user_id,buttons_template_message)
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
