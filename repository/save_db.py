import requests
import pymongo
import json
import sys
from models.User import LineUser
from linebot_config import APIConfig


config = APIConfig()

uri = 'mongodb://dev:dev1234@ds123181.mlab.com:23181/heroku_ptss9tm3'

client = pymongo.MongoClient(uri)
db = client.get_default_database()
PROVIDER = 'LINE'
VENDOR = ['雄獅', '可樂', '山富']
url_head =  config.ENDPOINT + "api/lineuser/"


def get_html(url):
    response = requests.request("GET", url)
    return response


def is_first_login(user_key):
    # 先把method開出來，到時候去搜尋FlightGo會員資料庫，確認會員是不是第一次使用
    url = url_head+user_key
    response = get_html(url)
    if response.status_code == 200:
        print(response.text == [])
        print(len(response.text))
        print(response.text)
        if len(response.text) <= 2 :
            isfirst = True
        else:
            isfirst = False
    else:
        isfirst = True
    print(isfirst)
    return isfirst

def get_user(user_key):
    # 先把method開出來，到時候去搜尋FlightGo會員資料庫，確認會員是不是第一次使用
    # url = "https://flightgo-dashboard-dev.herokuapp.com/api/lineuser/"+user_key
    # we use localhost in dev env now rather then remote
    url = url_head+user_key
    response = get_html(url)


def save_memberInfo_data(user_id, phoneNumber, email, gender, profile):
    # 將會員資料傳到後端，讓後端進行儲存
    # url = "http://localhost:3000/api/lineuser/"+user_id
    print("#save_memberInfo_data")
    headers = {
        'Content-Type': "application/json",
    }
    name = profile.display_name
    picture = profile.picture_url
    user = LineUser(user_id, name, email, gender, phoneNumber, picture)
    data = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "gender": user.gender,
        "phone_number": user.phone_number,
        "picture_url": user.picture_url,
        "favorite": ''
    }

    response = requests.request(
        "POST", config.ENDPOINT + "api/lineuser/", data=json.dumps(data), headers=headers)
    print(response.text)
    return response.json()


def save_favorite_questionnaire(user_key, favorite_list):
    # 將每位user 做的喜好旅遊類型問卷答案往後端儲存
    print(favorite_list[0])
    # we use localhost in dev env now rather then remote
    url = url_head+user_key

    response = get_html(url)
    data = response.json()
    print(data)
    
    if response.status_code == 200 and data:
        data.update({'favorite': favorite_list[1]})
        headers = {
            'Content-Type': "application/json",
        }
        response = requests.request(
            "PUT", config.ENDPOINT + "api/lineuser/"+user_key, data=json.dumps(data), headers=headers)



def save_message(event, message):
    user = get_user(event.source.user_id)
    if user is None:
        print('#no user exist')    
        return 'no user exist'
    print('#save_message')
    headers = {
        'Content-Type': "application/json",
    }
    data = {
        'user_id': event.source.user_id,
        'ask': {
            'replyToken': event.reply_token,
            'type': event.type,
            'timestamp': event.timestamp,
            'source_type': event.source.type,
            'source_user_id': event.source.user_id,
            'message_id': event.message.id,
            'mesage_type': event.message.type,
            'message_text': event.message.text,
            'vendor': VENDOR[2]  # e.g 山富
        },
        'reply': {
            'from': 'flightgo',  # it may from flightgo OR vendor name
            'type': message[0].type,
            'text': message[0].text
        }
    }
    print(config.ENDPOINT + "api/session")
    print(json.dumps(data))
    response = requests.request(
        "POST", config.ENDPOINT + "api/session", data=json.dumps(data), headers=headers)
    print(response.text)


def get_member_info(user_key):
    url = url_head + user_key
    response = get_html(url)
    print("response.text type :")
    print(type(response.text))
    print("response type :")
    print(type(response))
    return response.text