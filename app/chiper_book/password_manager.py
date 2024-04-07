from .encryption import encrypt, decrypt, hash_key, salt_hash_key
from .database import Database


class PasswordManager:
    def __init__(self):
        self.db = Database()

    # 判断密钥是否正确
    def is_valid_key(self, key):
        key_info = self.db.get_key()
        # print(key_info)
        if key_info is None:
            return False
        else:
            salt = key_info[0]  # 第一个元素是 salt
            stored_key_hash= key_info[1]  # 第二个元素是 key_salt_hash
            # print(salt)
            # print(stored_key_hash)
            provider_key_hash, _ = salt_hash_key(key, salt)
            # print(provider_key_hash)
            if provider_key_hash == stored_key_hash:
                return True
            else:
                return False


    # 设置主密钥，并将其 salt 和哈希值存储到数据库中
    def set_key(self, key):
        key_salt_hash, salt = salt_hash_key(key)
        self.db.store_key(key_salt_hash, salt)  # 添加当前用户名

    # 修改主密钥，并将其 salt 和哈希值存储到数据库中
    def reset_key(self, key):
        stored_key = self.db.get_key()  # 获取当前登录用户的主密钥
        if stored_key is not None:
            self.db.delete_key()  # 删除当前用户的主密钥
        self.set_key(key)

    # 生成一个新的密码，并将其加密后存储到数据库中
    def store_password(self, app_name, password, key_hash):
        encrypted_password = encrypt(key_hash, password)
        self.db.store_password(app_name, encrypted_password)  # 添加当前用户名

    # 获取指定应用的密码
    def get_password(self, app_name, key):
        result_password = self.db.get_password(app_name)  # 添加当前用户名
        # print(result_password)
        is_valid_key = self.is_valid_key(key)
        if not is_valid_key:
            return "Invalid key"
        elif result_password is None:
            return "No entry found for the given application name"
        else:
            key_hash = hash_key(key)

            return decrypt(key_hash, bytes(result_password[3]))
