import sqlite3
import pandas as pd

# 設定資料庫文件名稱
db_file = 'reservations.db'

# 連接到資料庫
conn = sqlite3.connect(db_file)

# 讀取 reservations 資料表
reservations_df = pd.read_sql_query("SELECT * FROM reservations", conn)
print("Reservations Table:")
print(reservations_df)

# 讀取 download_keys 資料表
download_keys_df = pd.read_sql_query("SELECT * FROM download_keys", conn)
print("\nDownload Keys Table:")
print(download_keys_df)

# 讀取 user_levels 資料表
user_levels_df = pd.read_sql_query("SELECT * FROM user_levels", conn)
print("\nUser Levels Table:")
print(user_levels_df)

# 關閉資料庫連接
conn.close()


