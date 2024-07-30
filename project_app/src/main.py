import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from gui import MainWindow  # Import your main GUI class

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 200, 200)
        self.setMaximumSize(200,200)
        self.setWindowTitle('First Time Login')
        self.setStyleSheet("background-color: #rgb(27, 29, 35);")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel('Login')
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("your name here")
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 1px solid gray;
                padding: 5px;
            }
        """)
        layout.addWidget(self.name_input)

        login = QPushButton('log me')
        login.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                border: none;
                padding: 10px;
                color: white;
            }
        """)
        login.clicked.connect(self.login)

        layout.addWidget(login)
        self.setLayout(layout)

    def login(self):
        name = self.name_input.text()
        if name:
            save_username(name)
            self.close()
            self.start_main_gui()
        else:
            print("Please enter a name")

    def start_main_gui(self):
        self.main_window = MainWindow()
        self.main_window.show()

def get_config_path():
    get_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))        
    return os.path.join(get_path, "config", "username.json")

def load_username():
    path_config = get_config_path()
    if os.path.exists(path_config):
        with open(path_config, 'r') as file:
            data = json.load(file)
        return data.get("username")
    return None

def save_username(username):
    path_config = get_config_path()
    os.makedirs(os.path.dirname(path_config), exist_ok=True)
    with open(path_config, 'w') as file:
        json.dump({"username": username}, file)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    username = load_username()
    if username:
        main_window = MainWindow()
        main_window.show()
    else:
        login_window = LoginWindow()
        login_window.show()
    
    sys.exit(app.exec())