# coding: utf-8
from PyQt5.QtCore import QObject


class Translator(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.cipher = self.tr('密码本')
        self.verifier = self.tr('程序正确性验证')
        self.flowDetec = self.tr('恶意流量检测')
        self.malDetec = self.tr('恶意软件检测')