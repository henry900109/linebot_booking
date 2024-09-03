# LINE Bot Booking System

這是一個基於 Flask 的 LINE Bot 預約系統，使用 Docker 進行容器化部署。該系統允許用戶通過 LINE Bot 進行預約、取消預約、查看預約等操作。

## 系統架構

1. **Flask 應用**：主要的 Web 應用程式，處理 LINE Bot 的請求和回應。
2. **LINE Bot**：與用戶進行互動，包括接收消息、處理回調和發送消息。
3. **資料庫**：用於存儲用戶資料、預約信息等。
4. **Docker**：容器化部署，簡化應用的部署和運行過程。

## 文件結構

- `app/`
  - `main.py`：Flask 應用的主入口點。
  - `utils/`
    - `database.py`：與資料庫交互的工具函式。
    - `line_bot.py`：處理 LINE Bot 的消息和回調事件。
    - `reservations.py`：處理預約相關操作的函式。
  - `templates/`
    - `member_login.html`：用戶登入的 HTML 模板。
  - `uwsgi.ini`：uWSGI 配置文件。
- `.env`：環境變數配置文件（不會提交至版本控制系統）。
- `Dockerfile`：Docker 配置文件，定義如何構建 Docker 映像。
- `docker-compose.yml`：Docker Compose 配置文件，用於管理多個容器的部署。
- `README.md`：專案文檔文件，提供專案的概覽和使用說明。

## 安裝和運行

### 1. 設置環境變數

創建 `.env` 文件並設置所需的環境變數，例如：

```env
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
LIFF_ID=your_liff_ID
host_url=host_url