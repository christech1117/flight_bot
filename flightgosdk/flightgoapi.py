import requests
import json
import sys
from models.User import LineUser
from linebot_config import APIConfig

config = APIConfig()



PROVIDER = 'LINE'
VENDOR = ['雄獅', '可樂', '山富']
url_head = config.ENDPOINT + "/lineUsers/userid/"
providerId = "U33d4b31a307907a59aa13c46c68e2919"


def get_html(url):
    response = requests.request("GET", url)
    return response


def is_first_login(user_key):
    # 先把method開出來，到時候去搜尋FlightGo會員資料庫，確認會員是不是第一次使用
    url = url_head + user_key
    response = get_html(url)
    if response.status_code == 200:
        print(response.text == [])
        print(len(response.text))
        print(response.text)
        if len(response.text) <= 2:
            isfirst = True
        else:
            isfirst = False
    else:
        isfirst = True
    print(isfirst)
    return isfirst

def save_member_info_data(user_id, phoneNumber, email, gender, profile):
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
        "userId": user.user_id,
        "name": user.name,
        "email": user.email,
        "gender": user.gender,
        "phone_number": user.phone_number,
        "picture_url": user.picture_url,
        "favorite": '',
        'age':'',
        'providerId':providerId
    }

    response = requests.request(
        "POST", config.ENDPOINT + "/lineUsers/", data=json.dumps(data), headers=headers)
    print(response.text)
    return response.json()


def save_favorite_questionnaire(user_key, favorite_list):
    # 將每位user 做的喜好旅遊類型問卷答案往後端儲存
    print(favorite_list[0])
    # we use localhost in dev env now rather then remote
    data = {
        "type": "favorite",
        "userId": user_key,
        "providerId": providerId,
        "content": {'favorite': favorite_list[1:-1]},
    }
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.request(
        "POST", config.ENDPOINT + "/questionnaires", data=json.dumps(data), headers=headers)
    print(response)

def save_message(event, message):
    print('#save_message')
    headers = {
        'Content-Type': "application/json",
    }
    data = {
        "message":message,
        "roomId":providerId+"_"+event.source.user_id,
        "isRead":"false",
        "isChatBotMode":"true",
        "sender":event.source.user_id,
        "recipient":providerId
    }
    print(json.dumps(data))
    response = requests.request(
        "POST", config.ENDPOINT + "/chatmessages", data=json.dumps(data), headers=headers)
    print(response.text)


def get_member_info(user_key):
    url = url_head + user_key
    response = get_html(url)
    print("response.text type :")
    print(type(response.text))
    print("response type :")
    print(type(response))
    return response.text