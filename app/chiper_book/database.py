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
                encrypted_password BYTEA NOT NULL,
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
        # print(salt)
        # print(key_salt_hash)
        sql = "INSERT INTO keys (username, key_salt_hash, salt) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (username, key_salt_hash, salt))
        self.conn.commit()

    # 从数据库中检索指定应用的密码信息
    def get_password(self, app_name):
        username = globals.username
        sql = "SELECT * FROM user_passwords WHERE username = %s AND app_name = %s"
        self.cursor.execute(sql, (username, app_name))
        result = self.cursor.fetchone()
        return result

    def get_key(self):
        username = globals.username
        sql = "SELECT salt, key_salt_hash FROM keys WHERE username = %s"
        self.cursor.execute(sql, (username,))
        result = self.cursor.fetchone()
        
        if result:
            salt = bytes(result[0])
            key_salt_hash = bytes(result[1])
            return salt, key_salt_hash
        else:
            return None

    # 获取指定用户的所有密码
    def get_all_passwords(self):
        username = globals.username
        sql = "SELECT * FROM user_passwords WHERE username = %s"
        self.cursor.execute(sql, (username,))
        results = self.cursor.fetchall()
        # print(results)
        return results

    # 判断数据库中是否存在指定用户
    def is_app_name_exists(self, app_name):
        username = globals.username
        sql = "SELECT * FROM user_passwords WHERE username = %s AND app_name = %s"
        self.cursor.execute(sql, (username, app_name))
        result = self.cursor.fetchone()
        return True if result else False

    # 从数据库中删除指定用户的密码信息
    def delete_password(self, app_name):
        username = globals.username
        sql = "DELETE FROM user_passwords WHERE username = %s AND app_name = %s"
        self.cursor.execute(sql, (username, app_name))
        self.conn.commit()

    # 从数据库中删除指定用户的主密钥信息
    def delete_key(self):
        username = globals.username
        sql = "DELETE FROM keys WHERE username = %s"
        self.cursor.execute(sql, (username,))
        self.conn.commit()

    def __del__(self):
        # 关闭游标和数据库连接
        self.cursor.close()
        self.conn.close()
