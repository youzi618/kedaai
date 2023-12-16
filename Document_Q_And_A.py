# -*- coding:utf-8 -*-
import hashlib
import base64
import hmac
import time
from urllib.parse import urlencode
import json
import websocket
import _thread as thread
import ssl

class Document_Q_And_A:
    def __init__(self, APPId, APISecret, TimeStamp, OriginUrl):
        self.appId = APPId
        self.apiSecret = APISecret
        self.timeStamp = TimeStamp
        self.originUrl = OriginUrl

    def get_origin_signature(self):
        m2 = hashlib.md5()
        data = bytes(self.appId + self.timeStamp, encoding="utf-8")
        m2.update(data)
        checkSum = m2.hexdigest()
        return checkSum



    def get_signature(self):
        # 获取原始签名
        signature_origin = self.get_origin_signature()
        # print(signature_origin)
        # 使用加密键加密文本
        signature = hmac.new(self.apiSecret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha1).digest()
        # base64密文编码
        signature = base64.b64encode(signature).decode(encoding='utf-8')
        # print(signature)
        return signature



    def get_header(self):
        signature = self.get_signature()
        header = {
            "Content-Type": "application/json",
            "appId": self.appId,
            "timestamp": self.timeStamp,
            "signature": signature
        }
        return header

    def get_url(self):
        signature = self.get_signature()
        header = {
            "appId": self.appId,
            "timestamp": self.timeStamp,
            "signature": signature
        }
        return self.originUrl + "?" + f'appId={self.appId}&timestamp={self.timeStamp}&signature={signature}'
        # 使用urlencode会导致签名乱码
        # return self.originUrl + "?" + urlencode(header)



    def get_body(self):
        data = {
            "chatExtends": {
                "wikiPromptTpl": "请将以下内容作为已知信息：\n<wikicontent>\n请根据以上内容回答用户的问题。\n问题:<wikiquestion>\n回答:",
                "wikiFilterScore": 65,
                "temperature": 0.5
            },
            "fileIds": [
                "a50c0e233213123123b95842b73c"
            ],
            "messages": [
                {
                    "role": "user",
                    "content": "如何理赔"
                },
                {
                    "role": "assistant",
                    "content": "您好，根据您提供的信息，理赔操作指引如下：\n\n1. 登录小程序，点击“理赔申请”。\n2. 选择对应保单。\n3. 上传理赔相关资料。\n4. 填写发票总金额。\n5. 填写银行账户，需精确到支行。\n6. 点击“提交”成功后，返回“理赔服务”界面，点选“理赔查询”，查看理赔进度和申请记录。\n7. 如有需要，点击“查看详情”，查看理赔详情和金额。\n\n请注意，如有严重既往症员工还请和HR部门及时报备沟通，如未及时报备，保险公司不承担相关责任。同时，索赔资料不齐全导致延迟赔付等问题也需要注意。"
                }
            ]
        }
        return data

# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print("关闭代码：", close_status_code)
    print("关闭原因：", close_msg)


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(ws.question)
    ws.send(data)

# 收到websocket消息的处理
def on_message(ws, message):
    # print(message)
    data = json.loads(message)
    code = data['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        content = data["content"]
        status = data["status"]
        # print(f'status = {status}')
        print(content, end='')
        if status == 2:
            ws.close()


if __name__ == '__main__':
    APPId = "******"
    APISecret = "******"
    curTime = str(int(time.time()))
    # curTime = "1690945325"
    OriginUrl = "wss://chatdoc.xfyun.cn/openapi/chat"
    document_Q_And_A = Document_Q_And_A(APPId, APISecret, curTime, OriginUrl)

    wsUrl = document_Q_And_A.get_url()
    print(wsUrl)
    headers = document_Q_And_A.get_header()
    body = document_Q_And_A.get_body()

    # 禁用WebSocket库的跟踪功能，使其不再输出详细的调试信息。
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = APPId
    ws.question = body
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


    # 文档问答成功