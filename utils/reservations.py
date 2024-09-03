import sqlite3
from datetime import datetime, timedelta
from linebot.models import ( 
    TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, 
    ConfirmTemplate, QuickReply, QuickReplyButton, PostbackAction
)
from .database import set_user_session ,generate_download_key
from flask import Flask, request, abort, send_file, render_template, jsonify
import csv
import os

host_url = os.getenv("host_url")


def get_user_level(user_id):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT level FROM user_levels WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "user"

def check_permission(user_id, required_level):
    USER_LEVELS = {
    "admin": 3,
    "manager": 2,
    "user": 1
}
    user_level = get_user_level(user_id)
    return USER_LEVELS.get(user_level, 0) >= USER_LEVELS.get(required_level, 0)

def show_available_dates(event,line_bot_api):
    dates = [datetime.now().date() + timedelta(days=i) for i in range(9)]
    date_groups = [dates[i:i+3] for i in range(0, len(dates), 3)]
    
    carousel_columns = []
    for group in date_groups:
        actions = [
            PostbackAction(
                label=date.strftime("%m/%d"),
                data=f"date_{date.strftime('%Y-%m-%d')}"
            ) for date in group
        ]
        
        column = CarouselColumn(
            thumbnail_image_url='https://example.com/calendar_icon.png',
            title='可預約日期',
            text='請選擇一個日期',
            actions=actions
        )
        carousel_columns.append(column)

    carousel_template = CarouselTemplate(columns=carousel_columns)
    template_message = TemplateSendMessage(
        alt_text='請選擇日期',
        template=carousel_template
    )

    line_bot_api.reply_message(event.reply_token, template_message)

def confirm_reservation(event, user_id, date, time,line_bot_api):
    expire_time = datetime.now() + timedelta(minutes=10)
    
    session_data = {
        'date': date,
        'time': time,
        'expire_time': expire_time.isoformat()
    }
    set_user_session(user_id, session_data, expire_time)
    
    confirm_template = ConfirmTemplate(
        text=f"您選擇的預約\n日期是：{date}\n時間是：{time}\n請確認是否要預約？\n(此確認鏈接在{expire_time.strftime('%H:%M:%S')}前有效)",
        actions=[
            PostbackAction(label="確認", data=f"confirm_{date}_{time}"),
            PostbackAction(label="取消", data=f"unconfirm__{date}_{time}")
        ]
    )
    template_message = TemplateSendMessage(
        alt_text="請確認您的預約",
        template=confirm_template
    )
    line_bot_api.reply_message(event.reply_token, template_message)

def show_available_times(event, date,line_bot_api):
    occupied_times = get_occupied_times(date)
    all_times = [f"{h:02d}:00" for h in range(9, 17)]
    available_times = [time for time in all_times if time not in occupied_times]

    quick_reply_buttons = [
        QuickReplyButton(action=PostbackAction(label=time, data=f"time_{date}_{time}"))
        for time in available_times
    ]

    text_message = TextSendMessage(
        text="請選擇時間",
        quick_reply=QuickReply(items=quick_reply_buttons)
    )

    line_bot_api.reply_message(event.reply_token, text_message)

def get_occupied_times(date):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT time FROM reservations WHERE date = ?", (date,))
    occupied_times = [row[0] for row in c.fetchall()]
    conn.close()
    return occupied_times

def make_reservation(event, user_id, date, time,line_bot_api):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    
    c.execute("SELECT user_id FROM reservations WHERE date = ? AND time = ?", (date, time))
    result = c.fetchone()
    
    if result:
        if result[0] == user_id:
            message = "你已預約該時段。"
        else:
            message = "該時段已被預約，請選擇其他時間。"
    else:
        try:
            c.execute("INSERT INTO reservations (user_id, date, time) VALUES (?, ?, ?)",
                      (user_id, date, time))
            c.execute("SELECT name, gender FROM user_levels WHERE user_id = ?", (user_id,))
            user_info = c.fetchone()

            conn.commit()
            conn.close()

            message = f"預約成功！\n日期：{date}\n時間：{time}\n感謝您使用我們的服務。"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        except Exception as e:
            conn.close()
            print(f'Error: {e}')
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="預約失敗，請稍後再試。"))

def show_user_reservations(event, user_id, line_bot_api,for_cancellation=False):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT date, time FROM reservations WHERE user_id = ? ORDER BY date, time", (user_id,))
    reservations = c.fetchall()
    conn.close()

    if not reservations:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="您目前沒有預約。")
        )
        return

    if for_cancellation:
        quick_reply_buttons = [
            QuickReplyButton(
                action=PostbackAction(label=f"{date} {time}", data=f"cancel_{date}_{time}")
            ) for date, time in reservations
        ]

        text_message = TextSendMessage(
            text="請選擇要取消的預約",
            quick_reply=QuickReply(items=quick_reply_buttons)
        )
    else:
        reservations_text = "您的預約：\n" + "\n".join([f"{date} {time}" for date, time in reservations])
        text_message = TextSendMessage(text=reservations_text)

    line_bot_api.reply_message(event.reply_token, text_message)

def cancel_reservation(event, user_id, date, time,line_bot_api):
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("DELETE FROM reservations WHERE user_id = ? AND date = ? AND time = ?",
              (user_id, date, time))
    conn.commit()
    conn.close()

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"已取消 {date} {time} 的預約。")
    )

def send_download_link(event,line_bot_api):
    key = generate_download_key()
    download_link = f'{host_url}/download_csv?key={key}'
    text_message = TextSendMessage(
        text=f"點擊下面的連結下載 CSV 檔案：\n{download_link}"
    )
    
    line_bot_api.reply_message(event.reply_token, text_message)

def download_csv():
    key = request.args.get('key')
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    c.execute("SELECT used FROM download_keys WHERE key = ?", (key,))
    result = c.fetchone()
    
    if result is None or result[0]:
        conn.close()
        abort(403)

    c.execute("UPDATE download_keys SET used = ? WHERE key = ?", (True, key))
    conn.commit()

    csv_filename = '../reservations.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'user_id', 'date', 'time'])
        c.execute("SELECT * FROM reservations")
        writer.writerows(c.fetchall())
    
    conn.close()
    return send_file(csv_filename, as_attachment=True)

def signup():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    gender = data.get('gender')
    user_id = data.get('userId')
    level = "member"
    
    conn = sqlite3.connect('reservations.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM user_levels WHERE user_id = ?", (user_id,))
    if c.fetchone()[0] > 0:
        conn.close()
        return jsonify({'success': False, 'message': '用戶已存在'})
    
    try:
        c.execute("INSERT INTO user_levels (user_id, name, phone, gender, level) VALUES (?, ?, ?, ?, ?)", 
                  (user_id, name, phone, gender, level))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        print(f'Error: {e}')
        return jsonify({'success': False, 'message': '註冊失敗'})