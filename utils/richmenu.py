import requests
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, PostbackAction
import os
from dotenv import load_dotenv

load_dotenv()
# 請替換為您的 LINE Bot 的 Channel Access Token
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))


# 創建圖文選單
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="Rich Menu 1",
    chat_bar_text="功能選單",
    areas=[
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
            action=PostbackAction(label='預約', data='action=booking')
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
            action=PostbackAction(label='取消預約', data='action=cancel')
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=1666, y=0, width=834, height=843),
            action=PostbackAction(label='已預約', data='action=booked')
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=843, width=1250, height=843),
            action=PostbackAction(label='未來功能1', data='action=f1')
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=843, width=1250, height=843),
            action=PostbackAction(label='未來功能2', data='action=f2')
        )
    ]
)


# 創建圖文選單
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# 上傳圖文選單圖片
with open("output.png", 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)

# 將圖文選單設置為預設選單
line_bot_api.set_default_rich_menu(rich_menu_id)

print("Rich menu created and set as default!")