from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QLineEdit, QMessageBox
from PyQt5.QtCore import QDate, QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator
from typing import Union

def MsgBox(icon: QMessageBox.Icon = QMessageBox.Icon.Information, text: str = 'ERROR', info: str = ''):
    """
    Displays a message box.

    Args:
        icon (QMessageBox.Icon): The icon to display in the message box.
        text (str): The main text of the message box.
        info (str): Additional information to display in the message box.
    
    Returns:
        int: The result of the message box execution.
    """
    msgbox = QMessageBox()
    msgbox.setIcon(icon)
    msgbox.setText(text)
    msgbox.setInformativeText(info)
    return msgbox.exec()

def CreateValidator(input: Union[QLineEdit, QDate], _: str, length: int):
    """
    Creates a regular expression validator for validating input.

    Args:
        input (Union[QLineEdit, QDate]): The input widget to apply the validator to.
        _: str: Not used. Placeholder for regex pattern.
        length (int): The maximum length of the input.

    Returns:
        None
    """
    return input.setValidator(QRegularExpressionValidator(QRegularExpression(r'[\w ]{0,' + str(length - 1) + '}\w{1}$')))


def CheckValidate(input: list):
    """
    Validates input fields.

    Args:
        input (list): A list of input fields to validate.

    Returns:
        bool: True if all input fields are valid, False otherwise.
    """
    # check all input fields are valid
    error_list = []
    for item in input:
        if not item.hasAcceptableInput():
            print(item.objectName())
            error_list.append(item.objectName())
    # if there is any objectName in error_list then exec QMessageBox else return True
    if error_list:
        MsgBox(text="Some input fields are invalid", info="Input Error: " + ", ".join(error_list))
    else:
        return True


class Connect2db:
    """
    A class for managing database connections.

    Attributes:
        dbname (str): The name of the database.
        connect_name (str): The name of the connection.
        db: The database connection object.
        connection_names (list): A list to store names of active connections.
    """

    def connect(self):
        """
        Connects to the database.
        """
        if self.current_connect_name not in self.connection_names:
            self.db = QSqlDatabase.addDatabase('QPSQL', self.current_connect_name)
            self.db.setHostName("127.0.0.1")
            self.db.setDatabaseName(self.dbname)
            self.db.setUserName("postgres")
            self.db.setPassword("469636")
            self.db.setPort(5432)
            self.connection_names.append(self.current_connect_name)
        else:
            self.disconect()
            MsgBox(QMessageBox.Icon.Critical, f'connection {self.current_connect_name} is still in use')
            self.connect()
            
    def __init__(self, dbname: str, connect_name: str):
        """
        Initializes a database connection.

        Args:
            dbname (str): The name of the database.
            connect_name (str): The name of the connection.
        """
        self.db = None
        self.dbname = dbname
        self.current_connect_name = connect_name
        self.connection_names = []
        self.disconect()
        self.connect()
    
    def disconect(self):
        """
        Disconnects from the database.
        """
        if QSqlDatabase.contains(self.current_connect_name):
                QSqlDatabase.removeDatabase(self.current_connect_name)


    def open(self):
        """
        Opens the database connection.
        """
        if self.db:
            if not self.db.open():
                error_message = self.db.lastError().text()
                MsgBox(QMessageBox.Icon.Critical, f'Failed to open database: {error_message}')         
    def errormsg(self):
        """
        Returns the last error message from the database.
        """
        return self.db.lastError().text()
    
    def close(self):
        """
        Closes the database connection.
        """
        if self.db and self.db.isOpen():
            self.db.close()
        else:
            MsgBox(QMessageBox.Icon.Critical, f'There is an error connecting to db: {self.errormsg()}')
    
    def query(self):
        """
        Executes a SQL query on the database.
        """
        if not self.db.isOpen():
            MsgBox(QMessageBox.Icon.Critical, f'There is an error connecting to db: {self.errormsg()}')
        return QSqlQuery(self.db)

    



