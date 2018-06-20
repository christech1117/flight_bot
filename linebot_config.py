
from linebot import (
    LineBotApi, WebhookHandler
)
import os

class linebotConfig():
    def __init__(self):
        self.token = os.environ['linetoken']
        self.screct = os.environ['linechannel']
    def get_LineBotAoi(self):
        return LineBotApi(self.token)
    def get_Handler(self):
        return WebhookHandler(self.screct)
