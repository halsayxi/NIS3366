from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPixmap

import os
import random, string
from werkzeug.security import generate_password_hash
from captcha.image import ImageCaptcha
from .register_window_ui import Ui_Form_register
from qframelesswindow import FramelessWindow
from .utils import Connect2db, CreateValidator, CheckValidate, MsgBox


class RegisterWidget(FramelessWindow):
    def __init__(self, login_widget:FramelessWindow, db: Connect2db):
        """
        Initializes the registration widget.

        Args:
            login_widget (FramelessWindow): The login widget.
            db (Connect2db): The database connection.
        """
        super().__init__()
        # Setup Ui designed by pyqt6 designer
        self.ui= Ui_Form_register()
        self.ui.setupUi(self)
        
        self.login_widget= login_widget

        # Connect to db
        self.db= db

        # Setup captcha 
        self.SetupCapcha()

        # Connect signal to slot
        self.ui.pushButton_register.clicked.connect(self.SignUp)
        self.ui.pushButton_refresh.clicked.connect(self.SetupCapcha)
        self.ui.lineEdit_username.editingFinished.connect(self.DuplicateUsername)
        self.ui.lineEdit_password_2.editingFinished.connect(self.ComparePassword)
        self.ui.pushButton_cancel.clicked.connect(self.CancelRegister)

        # Create Validators
        CreateValidator(self.ui.lineEdit_username, str, 50)
        CreateValidator(self.ui.lineEdit_password_1, str, 16)
        CreateValidator(self.ui.lineEdit_password_2, str, 16)

    def SetupCapcha(self):
        """
        Sets up captcha and pixmap.
        """
        try:
            os.remove('app/login_register/captcha/captcha.png')
        except:
            pass
        self.captcha= ''.join(random.choices(string.digits, k= 5))
        self.captcha_img= ImageCaptcha().write(self.captcha, 'app/login_register/captcha/captcha.png')
        self.ui.label_captcha_pixmap.setPixmap(QPixmap('app/login_register/captcha/captcha.png'))

    

    def SignUp(self):
        # first check if captcha is correct
        if not self.ui.lineEdit_captcha.text() == str(self.captcha):
            MsgBox(text="验证码错误...")
            self.ui.lineEdit_captcha.clear()
            self.SetupCapcha()

        # check if input field is valid
        else: 
            if CheckValidate([self.ui.lineEdit_username]):
                # Check if username is valid before attempting to open a database connection
                self.db.open()
                
                # Check if the 'users' table exists, if not create it
                query_check = self.db.query()
                query_check.exec("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')")
                    
                # Handle query result
                if query_check.next():
                    table_exists = query_check.value(0)
                        
                    if not table_exists:
                        # Create the 'users' table if it doesn't exist
                        query_create = self.db.query()
                        query_create.exec("""
                            CREATE TABLE users (
                                id SERIAL PRIMARY KEY,
                                username VARCHAR(50) UNIQUE NOT NULL,
                                password VARCHAR(255) NOT NULL
                            );
                        """)

                # Execute insert operation
                query_insert = self.db.query()
                query_insert.exec(f"INSERT INTO users (username, password) VALUES ('{self.ui.lineEdit_username.text()}', '{generate_password_hash(self.ui.lineEdit_password_1.text())}')")
                MsgBox(text="注册成功！欢迎进入软件安全管家")

                # remove captcha.png and close the RegisterForm
                os.remove('app/login_register/captcha/captcha.png')
                self.close()
                self.login_widget.show()
                self.db.close()
                 

    def DuplicateUsername(self):
        """
        Checks if the entered username already exists in the database.
        """
        self.db.open()
        
        query= self.db.query()
        query.exec(f"SELECT * FROM users WHERE username= '{self.ui.lineEdit_username.text()}'")
        if query.next():
            self.ui.lineEdit_username.clear()
            MsgBox(text="该用户名已被使用...")

        self.db.close()
        

    def ComparePassword(self):
        """
        Compares the two password inputs and prompts a warning if they are not identical.
        """
        if not self.ui.lineEdit_password_1.text() == self.ui.lineEdit_password_2.text():
            self.ui.lineEdit_password_1.clear()
            self.ui.lineEdit_password_2.clear()
            MsgBox(QMessageBox.Icon.Warning, "再次输入的密码不一致...")

    def CancelRegister(self):
        """
        Closes the registration form and shows the login widget.
        """
        self.close()
        self.login_widget.show()
        