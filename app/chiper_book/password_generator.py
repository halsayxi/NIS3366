import string
import random


def generate_password(length=8, has_uppercase=True, has_lowercase=True, has_digits=True, has_special_chars=True):
    # 创建一个空的字符集
    chars = ''

    # 根据参数添加相应的字符到字符集中
    if has_uppercase:
        chars += string.ascii_uppercase
    if has_lowercase:
        chars += string.ascii_lowercase
    if has_digits:
        chars += string.digits
    if has_special_chars:
        chars += string.punctuation

    # 从字符集中随机选择字符，生成密码
    password = ''.join(random.choice(chars) for _ in range(length))

    return password

