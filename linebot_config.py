
from linebot import (
    LineBotApi, WebhookHandler
)
import os

class linebotConfig:
    '''config 使用說明
        可自己git clone到本機端之後，使用Ngrok
        並將自己設定的Dev Line bot  token 跟  channel screct 填到
        self.token = token
        self.screct = channel screct
        '''
    def __init__(self):
        self.token = os.environ['linetoken']
        self.screct = os.environ['linechannel']
        # self.token = "9BCweAdC1k5sE+h6cOsEEFlqt5AnCyHbmMkjh5Tx3DvGYMCN6XS+pG2E+1o4i/3Z0EbsbGzIOcmQH7o+UguZr42KsEqwCP0kNb1C0A+jPCRraX8Iv5po87utrmgv5KqdA9kzjn1fSyTDkDzlmQk4hQdB04t89/1O/w1cDnyilFU="
        # self.screct = "dfeba0eb2c605954b39823c88831c8a1"

    def get_LineBotAoi(self):
        print(self.token)
        return LineBotApi(self.token)
    def get_Handler(self):
        return WebhookHandler(self.screct)

class APIConfig:

    def __init__(self):
        self.ENDPOINT = "https://flightgo-dashboard.herokuapp.com/"
        #self.ENDPOINT = "http://localhost:3000/"
