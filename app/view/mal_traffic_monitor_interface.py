# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLabel, QSizePolicy, QFileDialog
from PyQt5.QtGui import QFont
from qfluentwidgets import (PushButton, StrongBodyLabel)

from ..common.translator import Translator
from .gallery_interface import GalleryInterface
from ..TrafficDetection.get_badx import GetBadx
from ..TrafficDetection.get_feature import GetFeature

import os
import joblib


class MalTrafficMonitorInterface(GalleryInterface):
    """ mal traffic monitor interface """

    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title=t.flowDetec,
            subtitle='Malicious Traffic Monitoring System',
            parent=parent
        )
        self.setObjectName('MalTrafficMonitorInterface')

        self.titleLabel = StrongBodyLabel('选择pcap文件上传，检测流量的安全性。', self)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)

        self.card = QFrame(self)
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.card.setFixedHeight(200)
        self.vBoxLayout.addWidget(self.card)

        self.card_layout = QVBoxLayout(self.card)

        self.result = StrongBodyLabel(self.card)
        self.result.setText('暂无检测结果。')
        self.card_layout.addWidget(self.result, 0, Qt.AlignHCenter)

        self.resLabel = QLabel(self.card)
        self.resLabel.setFont(QFont('Microsoft YaHei', 15, QFont.DemiBold))
        self.card_layout.addWidget(self.resLabel, 0, Qt.AlignHCenter)

        self.file_button = PushButton(self.tr('选择文件'))
        self.file_button.clicked.connect(self.openFileDialog)
        self.file_button.setFixedSize(100, 35)
        self.vBoxLayout.addWidget(self.file_button, 0, Qt.AlignHCenter)


    def openFileDialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, '选择文件', '', 'pcap Files (*.pcap)')
        if filename:
            self.judge(filename)

    def judge(self, filename):
        if not os.path.exists(filename):
            print("{} does not exist".format(filename))
        self.result.setText('正在检测文件，请稍等...')

        csv_path = './app/TrafficDetection/dataset/badx.csv'
        get_badx=GetBadx(csv_path,filename,20*50)
        get_badx.get()
        x=GetFeature().MakeFeatures(csv_path)
        clf = joblib.load('./app/TrafficDetection/best_model.pkl')       # 加载已保存的模型

        self.result.setText('{}文件'.format(os.path.basename(filename)))
        if clf.predict(x).all():
            self.resLabel.setText('安全')
            self.resLabel.setStyleSheet('color: green')
        else:
            self.resLabel.setText('不安全')
            self.resLabel.setStyleSheet('color: red')

