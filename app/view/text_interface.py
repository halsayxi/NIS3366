# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QCompleter, QListWidgetItem, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout

from qfluentwidgets import (PasswordLineEdit, ListWidget,
                            PushButton, MessageBoxBase,
                            SubtitleLabel, LineEdit, Dialog, CheckBox)

from .gallery_interface import GalleryInterface
from ..common.translator import Translator
from app.chiper_book.encryption import hash_key
from app.chiper_book.password_manager import PasswordManager
from app.chiper_book.database import Database
from app.chiper_book.password_generator import generate_password

import threading


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

        self.user_input = None
        self.password_manager = PasswordManager()
        self.db = Database()

        self.is_valid_key = False

        # password line edit
        passwordLineEdit = PasswordLineEdit(self)
        passwordLineEdit.setFixedWidth(230)
        passwordLineEdit.setPlaceholderText(self.tr("Enter your password"))
        self.addExampleCard(
            title=self.tr("A password line edit"),
            widget=passwordLineEdit,
            sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/text/line_edit/demo.py'
        )

        self.listWidget = ListWidget()

        stands = ["QQ", "WeChat", "YouTube", "Twitter", "GitHUb"]

        # 添加列表项
        for stand in stands:
            # 创建一个新的QWidget
            widget = QWidget()
            layout = QHBoxLayout(widget)

            # 创建一个QLabel和一个QPushButton
            label = QLabel(stand)
            button = PushButton("查看密钥")
            button.clicked.connect(lambda checked, stand=stand: self.get_password(stand))

            # 将QLabel和QPushButton添加到布局中
            layout.addWidget(label)
            layout.addWidget(button)

            # 创建一个QListWidgetItem，并将QWidget设置为其widget
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

        self.listWidget.setFixedHeight(500)
        self.vBoxLayout.addWidget(self.listWidget)


        # 创建一个PushButton对象
        self.button = PushButton(self.tr('创建新密钥'))
        self.button.clicked.connect(self.new_password)
        self.vBoxLayout.addWidget(self.button)

    def new_password(self):
        w = GeneratePassword(self)
        if w.exec():
            print('确认')
        else:
            print('取消')

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


class GetKeyMessage(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('请输入密钥key')
        self.urlLineEdit = LineEdit()

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
        self.urlLineEdit = LineEdit()

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
        self.checkBox = CheckBox("Text")

        # 选中复选框
        self.checkBox.setChecked(True)

        # 监听复选框状态改变信号
        self.checkBox.stateChanged.connect(lambda: print(self.checkBox.isChecked()))

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.checkBox)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
