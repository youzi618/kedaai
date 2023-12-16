from flask import Flask, render_template
from flask_socketio import SocketIO
import SparkApi
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
socketio = SocketIO(app, message_queue=None)  # 添加 message_queue=None

appid = 'dcb34762'
api_secret = 'YmJlZmU3YmY1ZTQxZDg5NTk0YTM2YzJi'
api_key = '6e1b2fea859cee4beb7d9baf9027f22c'
domain = "generalv3"
Spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"
wang = {"name": "xiaohu"}
text = []

def getText(role, content):
    jsoncon = {"role": role, "content": content}
    text.append(jsoncon)
    return text

def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

def checklen(text):
    while getlength(text) > 8000:
        del text[0]
    return text

executor = ThreadPoolExecutor()

@app.route('/')
def home():
    return render_template('wang.html', wang=wang)

@socketio.on('send_message')
def handle_message(data):
    user_message = data['message']
    question = checklen(getText("user", user_message))

    def process_and_respond():
        SparkApi.answer = ""
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        getText("assistant", SparkApi.answer)
        socketio.emit('receive_message', {'reply': SparkApi.answer})

    executor.submit(process_and_respond)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)