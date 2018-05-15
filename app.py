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
import os

#import custom function
from linotravel_air_ticket_info  import find_air_ticket_info 
app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.environ['linetoken'])
# Channel Secret
handler = WebhookHandler(os.environ['linechannel'])

#======================parameter==================
session_dict = {}
session_second_list = []
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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    user_key = event.source.user_id
    if (user_key not in session_dict) :
        if(('搜尋機票' in event.message.text) or ('查詢機票' in event.message.text)):
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問出發地點 ?  (例如:台北、TPE)"   
        else:
            message_text_tmp = "抱歉目前僅提供搜尋機票功能，可打 搜尋機票 即可搜尋機票"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message)
    elif (len(session_dict[user_key]) == 1):
        if(event.message.text in region_list ):
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問目的地 ?  (例如:首爾)"   
        else:
            message_text_tmp = "很抱歉，請輸入正確的出發地點，如機場或是國家"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message)
    elif (len(session_dict[user_key]) == 2):
        if(event.message.text in region_list ):
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問出發日期? (日期格式 :2018年5月1號 請打 20180501 )"  
        else:
            message_text_tmp = "很抱歉，請輸入正確的目的地，如機場或是國家"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message)    
    elif (len(session_dict[user_key]) == 3): 
        if(event.message.text == '20180531'):
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問回國日期? (日期格式 :2018年5月1號 請打 20180501 )"  
        else:
            message_text_tmp = "很抱歉，請輸入正確的日期格式，:例如2018年5月1號 請打 20180501"
        message = TextSendMessage(text=message_text_tmp)        
        replay_message(event,message)
    elif (len(session_dict[user_key]) == 4): 
        if(event.message.text == '20180608'):
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "搜尋中，請稍後"
            message = TextSendMessage(text=message_text_tmp)        
            replay_message(event,message)
            push_tickets_info = TextSendMessage(text=search_air_tickest()) 
            push_message(event,push_tickets_info)    
        else:
            message_text_tmp = "很抱歉，請輸入正確的日期格式，:例如2018年5月1號 請打 20180501"
            message = TextSendMessage(text=message_text_tmp)        
            replay_message(event,message)
    else:
        message = TextSendMessage(text="程式目前維護中，請見諒")        
        replay_message(event,message)

def replay_message(event,message):
    line_bot_api.reply_message(
        event.reply_token,message)
        
def push_message(event,message):
    line_bot_api.push_message(
        event.source.user_id,
        message)        

def search_air_tickest():
    keys_list = ["Depart_tickets","Arrive_tickets"]
    tickets_keys = ['ArriveAirport','ArriveDate','DepartAirport','DepartDate','SellSeat','TotalFare']
    tickets_info = find_air_ticket_info()
    tickets_text = ""
    for item in tickets_info.keys():
        tickets_text += "================去程================\n"
        tickets_text += "出發地點"+tickets_info[item][keys_list[0]]['DepartAirport']+'\n'
        tickets_text += "出發時間"+tickets_info[item][keys_list[0]]['DepartDate']+'\n'
        tickets_text += "抵達地點"+tickets_info[item][keys_list[0]]['ArriveAirport']+'\n'
        tickets_text += "抵達時間"+tickets_info[item][keys_list[0]]['ArriveDate']+'\n'
        tickets_text += "================回程================\n"
        tickets_text += "出發地點"+tickets_info[item][keys_list[1]]['DepartAirport']+'\n'
        tickets_text += "出發時間"+tickets_info[item][keys_list[1]]['DepartDate']+'\n'
        tickets_text += "抵達地點"+tickets_info[item][keys_list[1]]['ArriveAirport']+'\n'
        tickets_text += "抵達時間"+tickets_info[item][keys_list[1]]['ArriveDate']+'\n'
        tickets_text += "================票價================\n"
        tickets_text += "每位大人含稅價格:"+tickets_info[item][keys_list[1]]['TotalFare']+'\n'
    return tickets_text
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
