# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QCompleter, QListWidgetItem, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout

from qfluentwidgets import (PasswordLineEdit, ListWidget, SpinBox,
                            PushButton, MessageBoxBase,
                            SubtitleLabel, LineEdit, Dialog, CheckBox)

from .gallery_interface import GalleryInterface
from ..common.translator import Translator
from app.chiper_book.encryption import hash_key
from app.chiper_book.password_manager import PasswordManager
from app.chiper_book.database import Database
from app.chiper_book.password_generator import generate_password


class TextInterface(GalleryInterface):
    """ Text interface """

    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title=t.text,
            subtitle="Password Management System",
            parent=parent
        )
        self.setObjectName('PasswordManagerSystem')

        self.password_manager = PasswordManager()
        self.db = Database()
        self.is_valid_key = False
        self.user_input = None

        self.listWidget = ListWidget()
        self.load_passwords()

        self.listWidget.setFixedHeight(500)
        self.vBoxLayout.addWidget(self.listWidget)

        self.button = PushButton(self.tr('创建新密码'))
        self.button.clicked.connect(self.new_password)
        self.button.setMaximumWidth(200)
        self.vBoxLayout.addWidget(self.button)

    def new_password(self):
        w = GetKeyMessage(self)
        if w.exec():
            key = w.urlLineEdit.text()
            self.is_valid_key = self.password_manager.is_valid_key(key)
        else:
            return
        w = GeneratePassword(self)
        if not self.is_valid_key:
            w = Dialog("ERROR", "密钥错误")
            if w.exec():
                print('确认')
            else:
                print('取消')
            return

        if w.exec():
            uppercase = w.uppercase.isChecked()
            lowercase = w.lowercase.isChecked()
            has_digits = w.has_digits.isChecked()
            has_special_chars = w.has_special_chars.isChecked()
            length = int(w.length.text())
            app_name = w.app_name.text()
            key_hash = hash_key(key)

            # 检查是否至少选择了一个字符种类
            if not (uppercase or lowercase or has_digits or has_special_chars):
                w = Dialog("ERROR", "请至少选择一个字符种类")
                if w.exec():
                    print('确认')
                else:
                    print('取消')
                return

            if self.db.is_app_name_exists(app_name):
                w = Dialog("ERROR", "应用已存在")
                if w.exec():
                    print('确认')
                else:
                    print('取消')
                return
            else:
                password = generate_password(length=length, has_uppercase=uppercase, has_lowercase=lowercase,
                                             has_digits=has_digits, has_special_chars=has_special_chars)
                self.password_manager.store_password(app_name, password, key_hash)
                self.load_passwords()

    def initialize_key(self):
        w = InitializeKeyMessage(self)
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        if w.exec():
            key = w.urlLineEdit.text()
            self.password_manager.set_key(key)

    def get_password(self, app_name):
        w = GetKeyMessage(self)
        if not self.db.get_key():
            self.initialize_key()
        if w.exec():
            key = w.urlLineEdit.text()
            self.is_valid_key = self.password_manager.is_valid_key(key)
            if not self.is_valid_key:
                w = Dialog("ERROR", "密钥错误")
                if w.exec():
                    print('确认')
                else:
                    print('取消')
            else:
                encrypted_password = self.password_manager.get_password(app_name, key)
                w = Dialog("提示", "密钥: " + encrypted_password)
                if w.exec():
                    print('确认')
                else:
                    print('取消')
        else:
            return

    def delete_password(self, app_name):
        w = GetKeyMessage(self)
        if not self.db.get_key():
            self.initialize_key()
        if w.exec():
            key = w.urlLineEdit.text()
            self.is_valid_key = self.password_manager.is_valid_key(key)
            if not self.is_valid_key:
                w = Dialog("ERROR", "密钥错误")
                if w.exec():
                    print('确认')
                else:
                    print('取消')
            else:
                self.db.delete_password(app_name)
                self.load_passwords()
        else:
            return

    def load_passwords(self):
        self.listWidget.clear()  # 清空列表
        passwords = self.db.get_all_passwords()
        app_names = [password['app_name'] for password in passwords]  # 使用列表推导式获取所有app_name

        # 添加列表项
        for app_name in app_names:
            # 创建一个新的QWidget
            widget = QWidget()
            layout = QHBoxLayout(widget)

            # 创建一个QLabel和一个QPushButton
            label = QLabel(app_name)
            view_button = PushButton("查看密钥")
            delete_button = PushButton("删除密码")
            view_button.setMaximumWidth(150)
            delete_button.setMaximumWidth(150)
            view_button.clicked.connect(lambda checked, app_name=app_name: self.get_password(app_name))
            delete_button.clicked.connect(lambda checked, app_name=app_name: self.delete_password(app_name))

            # 将QLabel和QPushButton添加到布局中
            layout.addWidget(label)
            layout.addWidget(view_button)
            layout.addWidget(delete_button)

            # 创建一个QListWidgetItem，并将QWidget设置为其widget
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)


class GetKeyMessage(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('请输入密钥key')
        self.urlLineEdit = PasswordLineEdit()

        self.urlLineEdit.setPlaceholderText('输入密钥key')
        self.urlLineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)


class InitializeKeyMessage(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('当前未定义密钥！')
        self.urlLineEdit = PasswordLineEdit()

        self.urlLineEdit.setPlaceholderText('请输入密钥，务必记住它')
        self.urlLineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)


class GeneratePassword(MessageBoxBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('创建密码')

        self.app_name = LineEdit()
        self.app_name.setPlaceholderText("输入应用名")

        self.uppercase = CheckBox("包含大写字母")
        self.lowercase = CheckBox("包含小写字母")
        self.has_digits = CheckBox("包含数字")
        self.has_special_chars = CheckBox("包含特殊字符")

        self.length = SpinBox()
        self.length.setRange(6, 50)
        self.length.setValue(6)

        # 选中复选框
        self.uppercase.setChecked(True)
        self.lowercase.setChecked(True)
        self.has_digits.setChecked(True)
        self.has_special_chars.setChecked(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.app_name)
        self.viewLayout.addWidget(self.uppercase)
        self.viewLayout.addWidget(self.lowercase)
        self.viewLayout.addWidget(self.has_digits)
        self.viewLayout.addWidget(self.has_special_chars)
        self.viewLayout.addWidget(self.length)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
