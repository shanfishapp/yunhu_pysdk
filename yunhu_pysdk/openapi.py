from requests import get, post
from logger import Logger
from sdk import sdk
class Send:
    def __init__(self):
        self.token = sdk.get()
    def request(recvId, recvType, type, msg, parentId=None, button=[], batch=False):
        if batch:
            if type(recvId) == list:
                url = 