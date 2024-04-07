import psycopg2
from app import globals



class Database:
    def __init__(self):
        # 连接到 PostgreSQL 数据库
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="469636",
            host="127.0.0.1",
            port="5432"
        )
        self.cursor = self.conn.cursor()

        # 创建名为 "users" 的表，用于存储用户名和密码
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

        # 创建名为 "keys" 的表，用于存储每个用户的主密钥
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keys (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                key_salt_hash BYTEA NOT NULL,
                salt BYTEA NOT NULL
            )
            """
        )
        self.conn.commit()

        # 创建名为 "user_passwords" 的表，用于存储每个用户的密码
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_passwords (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                app_name VARCHAR(255) NOT NULL,
                encrypted_password TEXT NOT NULL,
                CONSTRAINT fk_username FOREIGN KEY (username) REFERENCES users(username)
            )
            """
        )
        self.conn.commit()

    # 将应用名和加密后的密码存储到数据库中
    def store_password(self, app_name, encrypted_password):
        username = globals.username
        sql = "INSERT INTO user_passwords (username, app_name, encrypted_password) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (username, app_name, encrypted_password))
        self.conn.commit()

    # 将主密钥存储到数据库中
    def store_key(self, key_salt_hash, salt):
        username = globals.username
        print(salt)
        print(key_salt_hash)
        sql = "INSERT INTO keys
