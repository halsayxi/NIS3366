# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon
from ..common.config import cfg, HELP_URL, REPO_URL, DESIGN_URL, FEEDBACK_URL
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
from ..common.style_sheet import StyleSheet


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('软件安全管家', self)
        self.banner = QPixmap('app/resource/images/header1.png')
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            'app/resource/images/logo.png',
            self.tr('开始入门'),
            self.tr('通过查看使用介绍视频，查阅使用方法和案例。'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub仓库'),
            self.tr(
                '软件的 GitHub 仓库，您可以在这里查看源代码。'),
            REPO_URL
        )

        self.linkCardView.addCard(
            FluentIcon.LABEL,
            self.tr('设计文档'),
            self.tr(
                '点击链接，开始了解我们软件的内部机制和设计理念。'),
            DESIGN_URL
        )

        self.linkCardView.addCard(
            FluentIcon.FEEDBACK,
            self.tr('发送反馈'),
            self.tr('通过提供反馈帮助我们改进软件安全管家。'),
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # init linear gradient effect
        gradient = QLinearGradient(0, 0, 0, h)

        # draw background color
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            
        painter.fillPath(path, QBrush(gradient))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """ load samples """
        basicInputView = SampleCardView(
            self.tr("功能"), self.view)
        basicInputView.addSampleCard(
            icon="app/resource/images/controls/Checkbox.png",
            title="恶意软件检测",
            content=self.tr(
                "运用大模型检测软件是否安全"),
            routeKey="MalwareDetectionInterface",
            index=0
        )
        basicInputView.addSampleCard(
            icon="app/resource/images/controls/Checkbox.png",
            title="恶意流量监测",
            content=self.tr("运用大模型检测流量是否安全"),
            routeKey="MalTrafficMonitorInterface",
            index=8
        )
        basicInputView.addSampleCard(
            icon="app/resource/images/controls/ComboBox.png",
            title="程序正确性验证",
            content=self.tr(
                "验证程序行为是否符合预期"),
            routeKey="verifierInterface",
            index=10
        )
        basicInputView.addSampleCard(
            icon="app/resource/images/controls/Button.png",
            title="密码本",
            content=self.tr(
                "密码管理"),
            routeKey="textInterface",
            index=12
        )
        '''
        basicInputView.addSampleCard(
            icon="app/resource/images/controls/HyperlinkButton.png",
            title="HyperlinkButton",
            content=self.tr(
                "A button that appears as hyperlink text, and can navigate to a URI or handle a Click event."),
            routeKey="basicInputInterface",
            index=18
        )
        basicInputView.addSampleCard(
            icon="app/resource/images/controls/RadioButton.png",
            title="RadioButton",
            content=self.tr(
                "A control that allows a user to select a single option from a group of options."),
            routeKey="basicInputInterface",
            index=19
        )
        '''
        
        self.vBoxLayout.addWidget(basicInputView)