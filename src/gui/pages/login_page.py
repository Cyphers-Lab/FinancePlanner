"""Login page for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QStackedWidget, QComboBox)
from PyQt5.QtCore import Qt

class LoginPage(QWidget):
    """Login page widget with login and registration forms."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel('Financial Planner')
        title.setStyleSheet('font-size: 24px; font-weight: bold; margin-bottom: 20px;')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create stacked widget for login/register forms
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create login form
        login_widget = QWidget()
        login_layout = QVBoxLayout(login_widget)
        login_layout.setAlignment(Qt.AlignCenter)
        
        # Login form fields
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        
        # Login button
        login_button = QPushButton('Login')
        login_button.clicked.connect(self.handle_login)
        login_layout.addWidget(login_button)
        
        # Switch to register button
        switch_to_register = QPushButton('Need an account? Register')
        switch_to_register.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(register_widget))
        login_layout.addWidget(switch_to_register)
        
        # Create register form
        register_widget = QWidget()
        register_layout = QVBoxLayout(register_widget)
        register_layout.setAlignment(Qt.AlignCenter)
        
        # Register form fields
        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText('Username')
        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText('Email')
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setPlaceholderText('Password')
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_confirm_password = QLineEdit()
        self.reg_confirm_password.setPlaceholderText('Confirm Password')
        self.reg_confirm_password.setEchoMode(QLineEdit.Password)
        
        # Currency selection
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel('Preferred Currency:'))
        self.currency_select = QComboBox()
        self.currency_select.addItems(['$', '£', '€', '¥'])
        currency_layout.addWidget(self.currency_select)
        
        register_layout.addWidget(self.reg_username_input)
        register_layout.addWidget(self.reg_email_input)
        register_layout.addWidget(self.reg_password_input)
        register_layout.addWidget(self.reg_confirm_password)
        register_layout.addLayout(currency_layout)
        
        # Register button
        register_button = QPushButton('Register')
        register_button.clicked.connect(self.handle_register)
        register_layout.addWidget(register_button)
        
        # Switch to login button
        switch_to_login = QPushButton('Already have an account? Login')
        switch_to_login.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(login_widget))
        register_layout.addWidget(switch_to_login)
        
        # Add forms to stacked widget
        self.stacked_widget.addWidget(login_widget)
        self.stacked_widget.addWidget(register_widget)
        
        # Set fixed width for better appearance
        self.setFixedWidth(400)
        
        # Style the page
        self.style_widgets()
        
    def style_widgets(self):
        """Apply styles to widgets."""
        input_style = """
            QLineEdit {
                padding: 8px;
                margin: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """
        
        button_style = """
            QPushButton {
                padding: 10px;
                margin: 5px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        
        link_button_style = """
            QPushButton {
                padding: 5px;
                margin: 5px;
                background-color: transparent;
                color: #2196F3;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #1976D2;
            }
        """
        
        # Apply styles
        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet(input_style)
            
        for widget in self.findChildren(QPushButton):
            if 'account' in widget.text().lower():
                widget.setStyleSheet(link_button_style)
            else:
                widget.setStyleSheet(button_style)
                
    def handle_login(self):
        """Handle login button click."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            self.main_window.show_error('Please fill in all fields')
            return
            
        if self.main_window.app.login(username, password):
            self.clear_inputs()
            self.main_window.handle_login_success()
        else:
            self.main_window.show_error('Invalid username or password')
            
    def handle_register(self):
        """Handle register button click."""
        username = self.reg_username_input.text()
        email = self.reg_email_input.text()
        password = self.reg_password_input.text()
        confirm_password = self.reg_confirm_password.text()
        
        if not all([username, email, password, confirm_password]):
            self.main_window.show_error('Please fill in all fields')
            return
            
        if password != confirm_password:
            self.main_window.show_error('Passwords do not match')
            return
            
        currency = self.currency_select.currentText()
        if self.main_window.app.register(username, email, password, currency):
            self.clear_inputs()
            self.main_window.handle_login_success()
        else:
            self.main_window.show_error('Registration failed')
            
    def clear_inputs(self):
        """Clear all input fields."""
        self.username_input.clear()
        self.password_input.clear()
        self.reg_username_input.clear()
        self.reg_email_input.clear()
        self.reg_password_input.clear()
        self.reg_confirm_password.clear()
        self.currency_select.setCurrentIndex(0)
