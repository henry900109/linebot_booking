from linebot.models import TextSendMessage
from datetime import datetime
from .database import get_user_level, is_user_registered, get_user_session, delete_user_session  # 使用相對路徑
from .reservations import (
    send_download_link, show_available_dates, show_available_times,
    confirm_reservation, make_reservation, show_user_reservations, cancel_reservation
)  # 使用相對路徑
import os
LIFF_ID = os.getenv("LIFF_ID")

USER_LEVELS = {
    "admin": 3,
    "manager": 2,
    "user": 1
}

def check_permission(user_id, required_level):
    user_level = get_user_level(user_id)
    return USER_LEVELS.get(user_level, 0) >= USER_LEVELS.get(required_level, 0)

def handle_message(event, line_bot_api):
    user_id = event.source.user_id
    text = event.message.text
    if text == '@下載報表':
        if check_permission(user_id, "manager"):
            send_download_link(event, line_bot_api)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="您沒有權限執行此操作。")
            )

def handle_postback(event, line_bot_api):
    user_id = event.source.user_id
    data = event.postback.data

    if data.startswith('date_'):
        date = data.split('_')[1]
        show_available_times(event, date, line_bot_api)
    elif data.startswith('time_'):
        date, time = data.split('_')[1], data.split('_')[2]
        confirm_reservation(event, user_id, date, time, line_bot_api)
    elif data.startswith('confirm_'):
        date, time = data.split('_')[1], data.split('_')[2]
        user_session = get_user_session(user_id)
        
        if user_session:
            expire_time = datetime.fromisoformat(user_session['expire_time'])
            if datetime.now() > expire_time:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="確認鏈接已過期，請重新選擇時間。")
                )
                delete_user_session(user_id)
            else:
                make_reservation(event, user_id, date, time, line_bot_api)
                delete_user_session(user_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無效的確認請求。")
            )
    elif data.startswith('unconfirm_'):
        user_session = get_user_session(user_id)
        if user_session:
            delete_user_session(user_id)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="預約已取消")
            )
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無效操作"))
    elif data.startswith('cancel_'):
        date, time = data.split('_')[1], data.split('_')[2]
        cancel_reservation(event, user_id, date, time, line_bot_api)
    elif data == 'action=booking':
        if is_user_registered(user_id):
            show_available_dates(event, line_bot_api)
        else:
            url = f"請註冊會員\nhttps://liff.line.me/{LIFF_ID}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=url))
    elif data == 'action=cancel':
        if is_user_registered(user_id):
            show_user_reservations(event, user_id, line_bot_api, for_cancellation=True)
        else:
            url = f"請註冊會員\nhttps://liff.line.me/{LIFF_ID}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=url))
    elif data == 'action=booked':
        if is_user_registered(user_id):
            show_user_reservations(event, user_id, line_bot_api)
        else:
            url = f"請註冊會員\nhttps://liff.line.me/{LIFF_ID}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=url))
    elif data == 'action=f1':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未來功能1尚在開發中。"))
    elif data == 'action=f2':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未來功能2尚在開發中。"))
