from PyQt5.QtWidgets import QWidget, QApplication

import sys
from werkzeug.security import check_password_hash
from .login_window_ui import Ui_Form_login
from app.view.main_window import MainWindow
from .register_window import RegisterWidget
from .utils import Connect2db
from qframelesswindow import FramelessWindow
from app import globals


class LoginWidget(FramelessWindow):
    """
    Widget for handling user login.

    Attributes:
        ui (Ui_Form_login): The UI form for the login window.
        db (Connect2db): Connection to the database.
        login_user (str): The username of the logged-in user.
    """
    def __init__(self):
        """
        Initialize the LoginWidget.
        """
        super().__init__()

        # Use Ui_Form_login from LoginForm designed by pyqt6 designer
        self.ui= Ui_Form_login()
        self.ui.setupUi(self)

        # Connect to db
        self.db= Connect2db(dbname='postgres', connect_name='test')
        
        # init a login user to None
        self.login_user= None

        # Connect signal to slot
        self.ui.pushButton_login.clicked.connect(self.LoginButton)
        self.ui.pushButton_register.clicked.connect(self.RegieterButton)
        

        # define shortcut
        self.ui.pushButton_login.setShortcut('Return')

        self.show()


    def LoginButton(self):
        """
        Handle the login button click event.
        Connects to the database and checks if the entered username and password are valid.
        """
        self.db.open()

        query= self.db.query()
        query.exec(f"SELECT * FROM users WHERE username= '{self.ui.lineEdit_username.text()}'")
        
        # if login user is in user table then jump to MainWindow
        if query.next():
            pwhash= query.value(2)
            print(pwhash)
            if check_password_hash(pwhash, self.ui.lineEdit_password.text()):
                self.login_user= self.ui.lineEdit_username.text()
                globals.username = self.ui.lineEdit_username.text()
                self.main_window= MainWindow() # pass LoginWidget and login_user to to Mainwindow
                self.close()
                self.main_window.show()
            else:
                self.ui.label_msg.setText('密码错误...')
        else:
            self.ui.label_msg.setText('用户名不存在...')
        self.ui.lineEdit_username.clear()
        self.ui.lineEdit_password.clear()
        
    
    def RegieterButton(self):
        """
        Handle the register button click event.
        Opens the register window for new user registration.
        """
        self.RegisterForm = RegisterWidget(self, self.db) # pass LoginWidget to RegisterWidget
        self.RegisterForm.show()
        self.close()
        
        

if __name__ == '__main__':
    app= QApplication(sys.argv)
    Login= LoginWidget()
    sys.exit(app.exec())
