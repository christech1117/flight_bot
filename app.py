from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent,ImageSendMessage,TemplateSendMessage,ButtonsTemplate,PostbackTemplateAction,PostbackEvent,MessageTemplateAction,URITemplateAction,DatetimePickerTemplateAction,
ImagemapSendMessage,MessageImagemapAction,ImagemapArea,URIImagemapAction,BaseSize,StickerMessage,StickerSendMessage
)
import os
import sys
import pymongo
import datetime
import json
import re
#import custom function
from linotravel_air_ticket_info  import find_air_ticket_info 
from travel4_craw_airticket_info import main_search_airticket_info,get_airticket_title_Info


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
ask_member_Info_session_dict = {}
region_list = ["台北","TPE","首爾","SEL","ICN",'東京成田','NRT']
type_of_return = "type = return" 
type_of_depart = "type = depart"
datetime_type = {type_of_depart:'depart_date',type_of_return:'return_date'}


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
    print(PostbackEvent)
    user_key = event.source.user_id
    print(event)
    print(event.postback.data)
    if(event.postback.data == 'reSearch = true'):
        session_dict[user_key] = ['重新搜尋航班']
        session_second_list = list(session_dict[user_key])
    elif(event.postback.data == type_of_depart )   :
        time = event.postback.params
        session_second_list = list(session_dict[user_key])
        time_tmp = {datetime_type[type_of_depart]:time['date']}
        session_second_list.append(time_tmp)
        session_dict[user_key] = list(session_second_list)
        message_text_tmp = "你選擇的日期為:"+time['date']
        message = TextSendMessage(text=message_text_tmp)
        push_message(user_key,message)
        push_message(event.source.user_id,choice_datatime(type_of_return))
    elif(event.postback.data == type_of_return )   :
        time = event.postback.params
        session_second_list = list(session_dict[user_key])
        time_tmp = {datetime_type[type_of_return]: time['date']}
        print(session_dict[user_key])
        if(time['date'] >= session_dict[user_key][-1][datetime_type[type_of_depart]]):
            session_second_list.append(time_tmp)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "你選擇的回國日期為:" + time['date']
            message = TextSendMessage(text=message_text_tmp)
            push_message(user_key, message)
            message_text_tmp = "搜尋中，請稍後"
            message = TextSendMessage(text=message_text_tmp)
            push_message(event.source.user_id,message)
            #search_air_tickest(event)
            search_airticket_in_travel4(session_dict, user_key)
        else:
            message_text_tmp = "你選擇的回國日期小於出國日期，請重新選擇"
            message = TextSendMessage(text=message_text_tmp)
            push_message(event.source.user_id, message)
            push_message(event.source.user_id, choice_datatime(type_of_return))
@handler.add(FollowEvent)
def handle_FollowEvent(event):
    print("Follow event")
    global ask_member_Info_session_dict
    user_key = event.source.user_id
    profile = line_bot_api.get_profile(user_key)
    print(profile.display_name)
    print(profile.user_id)
    print(profile.picture_url)
    print(profile.status_message)
    if (is_first_Login(event)):
        print("First Login" + user_key)
        message_text_tmp = "Hi "+profile.display_name+"\n"
        message_text_tmp +="歡迎加入FlightGo!!\n\n"
        message_text_tmp +="可以使用FlightGo 來查詢機票。\n有任何問題也可直接詢問客服，FlightGo會立即通知真人客服來為您服務喔\n\n"
        message_text_tmp +="可以打#教學，即可秀出教學畫面唷\n\n"
        message_text_tmp +="為了提供更好的服務，請先填入以下基本資訊~"
        message = TextSendMessage(text=message_text_tmp)
        ask_member_Info_session_dict[user_key] = []
        message_slicker = StickerSendMessage(package_id = 1,sticker_id = 4)
        replay_event(event, [message,message_slicker])
        ask_paper_memberInfo(event)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    user_key = event.source.user_id
    profile = line_bot_api.get_profile(user_key)
    if(user_key in ask_member_Info_session_dict):
        ask_paper_memberInfo(event)
    elif ("廣告" == event.message.text):
        push_ads(user_key)
    elif (user_key not in session_dict):
        if ('搜尋機票' == event.message.text) or ('重新搜尋航班' == event.message.text ):
            search_air_info_session(event)
    elif(len(session_dict[user_key]) >= 1):
        search_air_info_session(event)
    else:
        other_session(event)

def search_air_info_session(event):
    user_key = event.source.user_id
    if ('重新搜尋航班' in event.message.text):
        session_dict[user_key] = []
        session_second_list = list(session_dict[user_key])
        session_second_list.append(event.message.text)
        print("輸入重新搜尋，user text is :"+str(event.message.text))
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
            message_text_tmp = "請問出發日期?"
        else:
            message_text_tmp = "很抱歉，請輸入正確的目的地，如機場或是國家"
        message = TextSendMessage(text=message_text_tmp)
        replay_message(event,message)
        push_message(event.source.user_id,choice_datatime(type_of_depart))
    elif (len(session_dict[user_key]) == 3):
        if(event.message.text == '20180531'):
            session_second_list = list(session_dict[user_key])
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "請問回國日期?"
        else:
            message_text_tmp = "很抱歉，請輸入正確的日期格式，:例如2018年5月1號 請打 20180501"
        message = TextSendMessage(text=message_text_tmp)
        replay_message(event,message)
        push_message(event.source.user_id,choice_datatime(type_of_return))
    elif (len(session_dict[user_key]) == 4):
        if(event.message.text == '20180608'):
            session_second_list = list(session_dict[user_key])
            session_second_list.append(event.message.text)
            session_dict[user_key] = list(session_second_list)
            message_text_tmp = "搜尋中，請稍後"
            message = TextSendMessage(text=message_text_tmp)
            replay_message(event,message)
            #search_air_tickest(event)
            search_airticket_in_travel4(session_dict, user_key)
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
        other_session(event)

def other_session(event):
    message_slicker = StickerSendMessage(package_id=2, sticker_id=34)
    message = TextSendMessage(text="目前程式尚未開發出對應功能，有任何問題將交由真人客服為您服務")
    replay_message(event, [message,message_slicker])

def is_first_Login(event):
    #先把method開出來，到時候去搜尋FlightGo會員資料庫，確認會員是不是第一次使用
    isfirst =True
    return  isfirst
def replay_message(event,message):
    save_message(event)
    line_bot_api.reply_message(
        event.reply_token,message)


def replay_event(event, message):
    line_bot_api.reply_message(
        event.reply_token, message)

def push_message(user_id,message):
    line_bot_api.push_message(
        user_id,
        message)


def save_message(event):
    print(type(event))
    data = {
        'user_id': event.source.user_id,
        'id': event.message.id,
        'type': event.message.type,
        'text': event.message.text,
        't': json.dumps(event.message.__dict__)
    },
    message_collection = db['message'] # collection; it is created automatically when we insert.
    message_collection.insert_many(data) # Note that the insert method can take either an array or a single dict.


def choice_datatime(type):
    now_time = datetime.datetime.now().strftime("%Y-%m-%d")
    max_time_tmp = datetime.datetime.now()+datetime.timedelta(days=365)
    max_time = max_time_tmp.strftime("%Y-%m-%d")
    print(now_time)
    print(max_time)
    if(type == type_of_return):
        title_string =" 請選擇回國日期"
        text_string = "選擇日期"
    else:
        title_string =" 請選擇啟程日期"
        text_string = "選擇日期"
    buttons_template_message = TemplateSendMessage(
        alt_text='DatetimePicker',
        template=ButtonsTemplate(
            title=title_string,
            text=text_string,
            actions=[
                DatetimePickerTemplateAction(
                    label = title_string,
                    mode = "date",
                    data=type,
                    initial = now_time,
                    max="2018-10-30",
                    min="2018-06-04"
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
                    text='重新搜尋航班',
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
def search_airticket_in_travel4(session_dict,user_key):
    print(session_dict[user_key])
    print(session_dict[user_key][3][datetime_type[type_of_depart]].replace("-","/"))
    print(session_dict[user_key][4][datetime_type[type_of_return]].replace("-","/"))

    airplane_all_detal_info_dict = main_search_airticket_info(session_dict[user_key][1], session_dict[user_key][2], session_dict[user_key][3][datetime_type[type_of_depart]].replace("-","/"),
                               session_dict[user_key][4][datetime_type[type_of_return]].replace("-","/"),'Y','5')
    titlename =get_airticket_title_Info()
    count_limit =5
    count_tmp =0
    for keys in airplane_all_detal_info_dict:
        print(airplane_all_detal_info_dict[keys])
        tickets_text = ""
        if(count_tmp >=  count_limit):
            break
        for list_tmp in titlename:
            for keys_i in list_tmp:
                tickets_text += list_tmp[keys_i] +":"+"\n"+airplane_all_detal_info_dict[keys][keys_i]+"\n"
                if (keys_i == 'TakeTime'):
                    tickets_text += "=================\n"
        tickets_text+="================="
        push_tickets_info = TextSendMessage(text=tickets_text)
        push_message(user_key, push_tickets_info)
        count_tmp +=1

def get_ads_info():
    photo_url = 'https://github.com/housekeepbao/flight_bot/blob/master/images/travel_test_img.png?raw=true'
    link_url = 'https://www.google.com.tw/maps/place/%E5%8F%A4%E6%97%A9%E5%91%B3%E5%B0%8F%E5%90%83%E5%BA%97/@25.0629705,121.5012555,23.8z/data=!4m8!1m2!2m1!1z5Y-w5YyX5qmLIOe-jumjnw!3m4!1s0x3442a92298613293:0xcff4aac1356b306!8m2!3d25.0629585!4d121.50107?hl=zh-TW'
    actions = [
        URIImagemapAction(
            link_uri=link_url,
            area=ImagemapArea(
                x=0, y=0, width=520, height=1024
            )
        ),
        MessageImagemapAction(
            text='我是第二個區域',
            area=ImagemapArea(
                x=520, y=0, width=520, height=512
            )
        ),
        MessageImagemapAction(
            text='我是第三個區域',
            area=ImagemapArea(
                x=520, y=512, width=520, height=1024
            )
        )
    ]
    return photo_url,link_url,actions
def push_ads(user_id):
    #photo_url = 'https://github.com/housekeepbao/flight_bot/blob/master/images/travel_test_img.png?raw=true'
    #link_url = 'https://www.google.com.tw/maps/place/%E5%8F%A4%E6%97%A9%E5%91%B3%E5%B0%8F%E5%90%83%E5%BA%97/@25.0629705,121.5012555,23.8z/data=!4m8!1m2!2m1!1z5Y-w5YyX5qmLIOe-jumjnw!3m4!1s0x3442a92298613293:0xcff4aac1356b306!8m2!3d25.0629585!4d121.50107?hl=zh-TW'
    photo_url,link_url,action_list = get_ads_info()
    imagemap_message = ImagemapSendMessage(
        base_url=photo_url,
        alt_text='this is an imagemap',
        base_size=BaseSize(height=1024, width=1024),
        actions=action_list
    )
    push_message(user_id, imagemap_message)
def share_link_info(user_id):
    link_url = {
        "to": "{user id}",
        "messages": [{
            "type": "template",
            "altText": "Account Link",
            "template": {
                "type": "buttons",
                "text": "Account Link",
                "actions": [{
                    "type": "uri",
                    "label": "Account Link",
                    "uri": "http://example.com/link?linkToken=xxx"
                }]
            }
        }]
    }
    link_url_json =json.dumps(link_url)
    push_message(user_id, link_url_json)
def ask_paper_memberInfo(event):
    global ask_member_Info_session_dict
    user_key = event.source.user_id
    if(len(ask_member_Info_session_dict[user_key]) ==0):
        tmp_list = list(ask_member_Info_session_dict[user_key])
        tickets_text = "請輸入您的行動電話號碼 例如:09123456789"
        tmp_list.append("ask_session_start")
        ask_member_Info_session_dict[user_key] = list(tmp_list)
        push_tickets_info = TextSendMessage(text=tickets_text)
        push_message(user_key, push_tickets_info)
    elif (len(ask_member_Info_session_dict[user_key]) == 1):
        tmp_list = list(ask_member_Info_session_dict[user_key])
        string = event.message.text
        pattern = '\d+'
        re_string = re.match(pattern, string)
        if(re_string != None ):
            tmp_list.append(string)
            tickets_text = "請輸入您的電子信箱 例如:mymail@gmail.com"
            ask_member_Info_session_dict[user_key] = list(tmp_list)
        else:
            tickets_text = "輸入的電話號碼有錯，請重新輸入"
        push_tickets_info = TextSendMessage(text=tickets_text)
        push_message(user_key, push_tickets_info)
    elif (len(ask_member_Info_session_dict[user_key]) == 2):
        tmp_list = list(ask_member_Info_session_dict[user_key])
        string = event.message.text
        str_tmp2 = "^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$"
        re_string = re.match(str_tmp2, string)
        if(re_string!= None ):
            tmp_list.append(string)
            tickets_text  = TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='請問您的性別',
                                text='請選擇您的性別',
                                actions=[
                                    PostbackTemplateAction(
                                        label='男性',
                                        text='男性',
                                        data='male'
                                    ),
                                    PostbackTemplateAction(
                                        label='女性',
                                        text='女性',
                                        data='female'
                                    )
                                ]
                            )
                        )
            ask_member_Info_session_dict[user_key] = list(tmp_list)
            push_message(user_key, tickets_text)
        else:
            tickets_text = "輸入的電子信箱有誤，請重新輸入"
            push_tickets_info = TextSendMessage(text=tickets_text)
            push_message(user_key, push_tickets_info)
    elif (len(ask_member_Info_session_dict[user_key]) == 3):
        tmp_list = list(ask_member_Info_session_dict[user_key])
        string = event.message.text
        if(string == '男性') or (string == '女性'):
            tmp_list.apppend(string)
            ask_member_Info_session_dict[user_key] = list(tmp_list)
            tickets_text = "會員資料已輸入完畢。"
            push_tickets_info = TextSendMessage(text=tickets_text)
            message_slicker = StickerSendMessage(package_id=1, sticker_id=125)
            push_message(user_key, [push_tickets_info,message_slicker])
        else:
            tickets_text = "輸入性別錯誤，請重新輸入"
            push_tickets_info = TextSendMessage(text=tickets_text)
            tickets_text = TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='請問您的性別',
                    text='請選擇您的性別',
                    actions=[
                        PostbackTemplateAction(
                            label='男性',
                            text='男性',
                            data='male'
                        ),
                        PostbackTemplateAction(
                            label='女性',
                            text='女性',
                            data='female'
                        )
                    ]
                )
            )
            push_message(user_key, [push_tickets_info,tickets_text])

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
