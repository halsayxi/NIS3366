from pymongo import MongoClient


class Database:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['SecureVault']
        self.collection = self.db['UserPasswords']

    # 将应用名和加密后的密码存储到数据库中
    def store_password(self, app_name, encrypted_password):
        self.collection.insert_one({
            'type': 'password',
            'app_name': app_name,
            'encrypted_password': encrypted_password
        })

    # 将主密钥的salt哈希值存储到数据库中
    def store_key(self, key_salt_hash, salt):
        self.collection.insert_one({
            'type': 'key',
            'key_salt_hash': key_salt_hash,
            'salt': salt
        })

    # 从数据库中检索指定应用的信息
    def get_password(self, app_name):
        result = self.collection.find_one({'app_name': app_name, 'type': 'password'})
        return result if result else None

    def get_key(self):
        result = self.collection.find_one({'type': 'key'})
        return result if result else None

    # 获取所有类型为password的条目
    def get_all_passwords(self):
        return self.collection.find({'type': 'password'})

    # 判断数据库中是否有重名
    def is_app_name_exists(self, app_name):
        result = self.collection.find_one({'app_name': app_name})
        return True if result else False

    # 从数据库中删除某个密码
    def delete_password(self, app_name):
        self.db.collection.delete_one({'app_name': app_name})

    # 从数据库中删除密钥
    def delete_key(self):
        self.db.collection.delete_one({'type': 'key'})
