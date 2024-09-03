# 使用 Python 3.10 作為基礎映像
FROM python:3.10

# 設置工作目錄
WORKDIR /

# 複製 requirements.txt 到工作目錄
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製當前目錄內容到工作目錄
COPY . .

# 暴露端口
EXPOSE 9999

# 啟動 uWSGI 服務
CMD ["uwsgi", "--http", "0.0.0.0:9999", "--module", "main:app", "--processes", "4", "--threads", "2"]
