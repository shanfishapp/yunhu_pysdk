import sys

try:
    import requests
    from requests import Session
except ImportError:
    print("Error: requests module is not installed. Please install it by running:")
    print("pip install requests")
    sys.exit(1)

import json
from typing import Dict, Any
from io import BytesIO

class StreamMessageClient:
    def __init__(self, token: str, base_url: str = "https://chat-go.jwzhd.com/open-apis/v1/bot/send-stream"):
        """
        初始化流式消息客户端
        
        :param token: API token
        :param base_url: 基础URL，默认为官方API地址
        """
        self.base_url = base_url
        self.token = token
        self.session = Session()  # 使用正确的Session类
    
    def send_stream_message(
        self,
        recv_id: str,
        recv_type: str,
        content_type: str,
        content: bytes,
        chunk_size: int = 1024,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        发送流式消息
        
        :param recv_id: 接收消息对象ID
        :param recv_type: 接收对象类型 (user/group)
        :param content_type: 消息类型 (text/markdown)
        :param content: 消息内容字节流
        :param chunk_size: 分块大小，默认1024字节
        :param timeout: 超时时间，默认30秒
        :return: API响应结果
        """
        # 构建请求URL
        url = f"{self.base_url}?token={self.token}&recvId={recv_id}&recvType={recv_type}&contentType={content_type}"
        
        # 创建生成器函数用于流式传输
        def generate():
            buffer = BytesIO(content)
            while True:
                chunk = buffer.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        
        # 设置请求头
        headers = {
            "Transfer-Encoding": "chunked",
            "Content-Type": "text/plain"
        }
        
        try:
            # 发送流式请求
            response = self.session.post(
                url,
                headers=headers,
                data=generate(),
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "code": -1,
                "msg": f"请求失败: {str(e)}",
                "data": None
            }
    
    def send_stream_text(
        self,
        recv_id: str,
        recv_type: str,
        text: str,
        encoding: str = "utf-8",
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送流式文本消息
        
        :param recv_id: 接收消息对象ID
        :param recv_type: 接收对象类型 (user/group)
        :param text: 文本内容
        :param encoding: 编码格式，默认utf-8
        :param kwargs: 其他send_stream_message参数
        :return: API响应结果
        """
        return self.send_stream_message(
            recv_id=recv_id,
            recv_type=recv_type,
            content_type="text",
            content=text.encode(encoding),
            **kwargs
        )
    
    def send_stream_markdown(
        self,
        recv_id: str,
        recv_type: str,
        markdown: str,
        encoding: str = "utf-8",
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送流式Markdown消息
        
        :param recv_id: 接收消息对象ID
        :param recv_type: 接收对象类型 (user/group)
        :param markdown: Markdown内容
        :param encoding: 编码格式，默认utf-8
        :param kwargs: 其他send_stream_message参数
        :return: API响应结果
        """
        return self.send_stream_message(
            recv_id=recv_id,
            recv_type=recv_type,
            content_type="markdown",
            content=markdown.encode(encoding),
            **kwargs
        )

if __name__ == "__main__":
    try:
        # 初始化客户端
        client = StreamMessageClient(token="f5aa61f62c384e6bb533a5bda5211cb8")
        
        # 发送流式文本消息
        response = client.send_stream_text(
            recv_id="6300451",
            recv_type="user",
            text="这是一条流式文本消息"
        )
        print("响应结果:", response)
        
        # 发送流式Markdown消息
        markdown_content = """
        # 标题
        - 列表项1
        - 列表项2
        **加粗文本**
        """
        response = client.send_stream_markdown(
            recv_id="6300451",
            recv_type="user",
            markdown=markdown_content
        )
        print("响应结果:", response)
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
