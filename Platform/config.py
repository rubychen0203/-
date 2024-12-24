import os

class Config:
    SECRET_KEY = os.urandom(24) # 生成一個長度為 24 個字節的隨機字串作為密鑰，用於保護session資料。
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/platform_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
