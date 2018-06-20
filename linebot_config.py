
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
    def get_LineBotAoi(self):
        print(self.token)
        return LineBotApi(self.token)
    def get_Handler(self):
        return WebhookHandler(self.screct)
