import requests
import json
from sdk import sdk
from logger import Logger
logger = Logger()

class Send:
    def __init__(self):  # 添加了冒号
        self._token = sdk.get()
        self.logger = Logger()
    def requests_send(self, recvId, recvType, type, msg, button=[], batch: bool = False, parentId=None):
        url = "https://chat-go.jwzhd.com/open-apis/v1/bot/send?token=" + self._token  # 添加了等号
        
        if batch == True:
            if not isinstance(recvId, list):  # 使用 not 而不是 !
                self.logger.error("HTTP 发送消息 API 参数传递错误：当batch为True时，recvId必须为数组")
                return
            url = "https://chat-go.jwzhd.com/open-apis/v1/bot/batch_send?token=" + self._token
        
        
        key = type_switch(type)
        if type == 'md':
            type = 'markdown'
        json_content = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": type,
            "content": {
                key: msg
            }
        }
        
        if button:
            if is_valid_array(button):  # 修正拼写错误
                json_content['content']['buttons'] = button
            else:
                self.logger.error("HTTP 发送消息 API 参数传递错误：button必须为有效格式数组(格式请前往https://www.yhchat.com/document/400-410)")
        recvtype_check(recvType, "发送消息")
        if parentId:
            json_content['parentId'] = parentId
        
        headers = {"Content-Type": "application/json;charset=utf-8"}
        response = requests.post(url=url, headers=headers, json=json_content).json()  # 修正 headers 和 json 参数
        check_error(response, "发送消息")
        return response  # 返回响应对象
    def md(self, recvId, recvType, msg, button=[], parentId=None, batch=False):
        return self.requests_send(recvId, recvType, "md", msg, button, batch, parentId)
    def text(self, recvId, recvType, msg, button=[], parentId=None, batch=False):
        return self.requests_send(recvId, recvType, "text", msg, button, batch, parentId)
    def html(self, recvId, recvType, msg, button=[], parentId=None, batch=False):
        return self.requests_send(recvId, recvType, "html", msg, button, batch, parentId)
    def image(self, recvId, recvType, msg, button=[], parentId=None, batch=False):
        return self.requests_send(recvId, recvType, "image", msg, button, batch, parentId)
    def video(self, recvId, recvType, msg, button=[], parentId=None, batch=False):
        return self.requests_send(recvId, recvType, "video", msg, button, batch, parentId)
    def file(self, recvId, recvType, msg, button=[], parentId=None, batch=False):
        return self.requests_send(recvId, recvType, "file", msg, button, batch, parentId)

def is_valid_array(arr):
    if not isinstance(arr, list):
        return False
    if not arr:
        return False
    for item in arr:
        if not isinstance(item, dict):
            return False
        required_fields = {"text", "actionType"}
        if not required_fields.issubset(item.keys()):
            return False
    return True

def type_switch(type):
    return {
        "md": "text",
        "text": "text",
        "html": "text",
        "image": "imageKey",
        "video": "videoKey",
        "file": "fileKey"
    }.get(type, "未知类型")
def check_error(json, title):
    if json['code'] != 1:
        logger.error(f"HTTP API {title} 响应错误：错误码：{json['code']}，错误原因：{json['msg']}")
    else:
        logger.info(f"{title} API 调用成功")
class reply:
    """快捷回复，无需填入recvId和recvType"""
    def __init__(self):
        return
    
def recvtype_check(recvType, title):
    if recvType == "user":
        pass
    elif recvType == "group":
        pass
    else:
        logger.error(f"HTTP {title} API 参数传递错误：recvType必须为user/group")
        return

class Msg:  # 类名建议大写
    def __init__(self):
        self.token = sdk.get()
    
    def recall(self, recvId, recvType, msgId):
        url = "https://chat-go.jwzhd.com/open-apis/v1/bot/recall?token=" + self.token
        recvtype_check(recvType, "撤回消息")  # 假设这是类方法
        
        data = {
            "msgId": msgId,
            "chatId": recvId,
            "chatType": recvType
        }
        
        headers = {"Content-Type": "application/json;charset=utf-8"}  # 修正header格式
        
        # 使用json参数自动序列化，或使用data=json.dumps(data)
        response = requests.post(url, json=data, headers=headers).json()  
        check_error(response, title="撤回消息")
        return response
    
class Get:
    def __init__(self):
        self.token = sdk.get()
    def requests_get(self, recvId, recvType, type, num, msgId=None):
        base_url = "https://chat-go.jwzhd.com/open-apis/v1/bot/messages?token=" + self.token
        recvtype_check(recvType, "获取消息")
        if not isinstance(num, int):
            logger.error("HTTP 获取消息 API 参数传递错误：num必须为整数(int)")
        if type == "latest":
            url = base_url + f"&chat-id={recvId}&chat-type={recvType}&before={num}"
        elif type == "after":
            url = base_url + f"chat-id={recvId}&chat-type={recvType}&after={num}&message-id={msgId}"
        elif type == "before":
            url = base_url + f"chat-id={recvId}&chat-type={recvType}&before={num}&message-id={msgId}"
        response = requests.get(url, headers={"Content-Type": "application/json;charset=utf-8"}).json()
        check_error(response, "获取消息")
        return response
    def after(self, recvId, recvType, num, msgId):
        return self.requests_get(recvId, recvType, "after", num, msgId)
    def before(self, recvId, recvType, num, msgId):
        return self.requests_get(recvId, recvType, "before", num, msgId)
    def latest(self, recvId, recvType, num):
        return self.requests_get(recvId, recvType, "latest", num)

class Edit:
    def __init__(self):
        self.token = sdk.get()
    def requests_edit(self, recvId, recvType, type, msg, msgId, button=[]):
        key = type_switch(type)
        if type == 'md':
            type = 'markdown'
        recvtype_check(recvType, "编辑消息")
        url = "https://chat-go.jwzhd.com/open-apis/v1/bot/edit?token=" + self.token
        data = {
            "msgId": msgId,
            "recvId": recvId,
            "recvType": recvType,
            "contentType": type,
            "content": {
                key: msg
            }
        }
        if is_valid_array(button):
            data['content']['buttons'] = button
        else:
            logger.error("HTTP 编辑消息 API 参数传递错误：button必须为有效格式数组(格式请前往https://www.yhchat.com/document/400-410)")
        headers = {"Content-Type": "application/json;charset=utf-8"}
        response = requests.post(url=url, headers=headers, json=data).json()  # 修正 headers 和 json 参数
        check_error(response, "编辑消息")
        return response  # 返回响应对象
    def md(self, recvId, recvType, msg, msgId, button=[]):
        return self.requests_edit(recvId, recvType, "md", msg, msgId, button)
    def text(self, recvId, recvType, msg, msgId, button=[]):
        return self.requests_edit(recvId, recvType, "text", msg, msgId, button)
    def html(self, recvId, recvType, msg, msgId, button=[]):
        return self.requests_edit(recvId, recvType, "html", msg, msgId, button)
    def image(self, recvId, recvType, msg, msgId, button=[]):
        return self.requests_edit(recvId, recvType, "image", msg, msgId, button)
    def video(self, recvId, recvType, msg, msgId, button=[]):
        return self.requests_edit(recvId, recvType, "video", msg, msgId, button)
    def file(self, recvId, recvType, msg, msgId, button=[]):
        return self.requests_edit(recvId, recvType, "file", msg, msgId, button)
class Board:
    def __init__(self):
        self.token = sdk.get()
    def requests_board(self, recvId, recvType, type, msg, time=0, userId = None):
        url = "https://chat-go.jwzhd.com/open-apis/v1/bot/board?token=" + self.token
        headers = {"Content-Type": "application/json"}
        recvtype_check(recvType, "设置用户看板")
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": type,
            "content": msg
        }
        if time != 0:
            data['expireTime'] = time
        if userId != None:
            data['memberId'] = userId
        response = requests.post(url, json=data, headers=headers).json()
        check_error(response, "设置用户看板")
        return response
    def md(self, recvId, recvType, msg, time=0, userId=None):
        return self.requests_board(recvId, recvType, "markdown", msg, time, userId)
    def text(self, recvId, recvType, msg, time=0, userId=None):
        return self.requests_board(recvId, recvType, "text", msg, time, userId)
    def html(self, recvId, recvType, msg, time=0, userId=None):
        return self.requests_board(recvId, recvType, "html", msg, time, userId)
    def delete(self, recvId, recvType, userId=None):
        url = "https://chat-go.jwzhd.com/open-apis/v1/bot/board-dismiss?token=" + self.token
        headers = {"Content-Type": "application/json"}
        data = {
            "recvId": recvId,
            "recvType": recvType
        }
        if userId != None:
            data['memberId'] == userId
        response = requests.post(url, json=data, headers=headers).json()
        check_error(response, "取消用户看板")
        return response
    
class Board_All:
    def __init__(self):
        self.token = sdk.get()
    def requests_board_all(self, msg, type, time):
        url = "https://chat-go.jwzhd.com/open-apis/v1/bot/board-all-dismiss?token=" + self.token
        headers = {"Content-Type": "application/json"}
        data = {
            "contentType": type,
            "content": msg
        }
        if time != 0:
            data['expireTime'] == time
        response = requests.post(url, headers=headers, data=data).json()
        check_error(response, "设置全局看板")
        return response
    def md(self, msg, time=0):
        return self.requests_board_all(msg, "markdown", time)
    def text(self, msg, time=0):
        return self.requests_board_all(msg, "markdown", time)
    def html(self, msg, time=0):
        return self.requests_board_all(msg, "markdown", time)
    def delete(self):
        url = "https://chat-go.jwzhd.com/open-apis/v1/bot/board-all-dismiss?token=" + self.token
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers).json()
        check_error(response, "取消全局看板")
        return response
class Upload:
    def __init__(self):
        self.token = sdk.get()
    def requests_upload(self, file_path, type):
        if type == "image":
            url = "https://chat-go.jwzhd.com/open-apis/v1/image/upload?token=" + self.token
            title = "图片"
        elif type == "video":
            url = "https://chat-go.jwzhd.com/open-apis/v1/video/upload?token=" + self.token
            title = "视频"
        elif type == "file":
            url = "https://chat-go.jwzhd.com/open-apis/v1/file/upload?token=" + self.token
            title = "文件"
        
        files = [
            (type, open(file_path, 'rb'))
        ]
        response = requests.post(url, files=files).json()
        check_error(response, f"上传{title}")
        return response
    def image(self, file):
        return self.requests_upload(file, 'image')
    def video(self, file):
        return self.requests_upload(file, 'video')
    def file(self, file):
        return self.requests_upload(file, 'file')