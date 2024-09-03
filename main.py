import os
from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv
from utils.database import init_db
from utils.linebot import handle_message, handle_postback
from utils.reservations import download_csv, signup
from linebot.models import MessageEvent, TextMessage, PostbackEvent  # 加上這裡的 import 以確保 handler.add 裡的事件正確


load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
LIFF_ID = os.getenv("LIFF_ID")
init_db()

@app.route('/download_csv')
def download_csv_route():
    return download_csv()

@app.route("/member_login")
def hello():
    return render_template('member_login.html')

@app.route("/signup", methods=['POST'])
def signup_route():
    return signup()

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def message_handler(event):
    handle_message(event, line_bot_api)

@handler.add(PostbackEvent)
def postback_handler(event):
    handle_postback(event, line_bot_api)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9999, debug=True)