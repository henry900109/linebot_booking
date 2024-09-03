# 使用 Docker 構建一個名為 "linebotbooking:v1" 的映像檔，並從當前目錄的 Dockerfile 生成映像。
sudo docker build -t linebotbooking:v1 .

# 運行一個新的 Docker 容器，基於 "linebotbooking:v1" 映像。將容器的 9999 端口映射到主機的 9999 端口，並將容器命名為 "linebotbooking"。
sudo docker run -d -p 9999:9999 --name linebotbooking linebotbooking:v1

# 進入名為 "linebotbooking" 的 Docker 容器的終端，並使用 bash 進行交互。
# 注意：這行命令被註釋掉了，如果需要進入容器可以取消註釋。
# sudo docker exec -it linebotbooking /bin/bash

# 列出容器內部的文件和目錄。這行命令在容器內執行。
# 注意：這行命令也被註釋掉了，如果需要進入容器後列出文件可以取消註釋。
# ls

# 查看 `uwsgi.log` 日誌文件的實時輸出。這行命令在容器內執行。
# 注意：這行命令也被註釋掉了，應在容器內執行。
# tail uwsgi.log

# 實時查看名為 "linebotbooking" 的 Docker 容器的日誌輸出。
sudo docker logs -f linebotbooking

# 退出容器的終端會話。
exit
