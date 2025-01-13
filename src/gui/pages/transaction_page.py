"""Transaction management page for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QGridLayout, QLineEdit,
                           QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
                           QHeaderView)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

class TransactionPage(QWidget):
    """Transaction page for managing financial transactions."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel('Transaction Management')
        title.setStyleSheet('font-size: 24px; font-weight: bold;')
        header.addWidget(title)
        
        # Back button
        back_btn = QPushButton('Back to Dashboard')
        back_btn.clicked.connect(self.main_window.show_dashboard)
        back_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        header.addStretch()
        header.addWidget(back_btn)
        layout.addLayout(header)
        
        # Main content area
        content = QHBoxLayout()
        
        # Left side - Transaction Form and Table
        left_panel = QVBoxLayout()
        
        # Transaction creation form
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        form_layout = QGridLayout(form_frame)
        
        # Amount input
        form_layout.addWidget(QLabel('Amount:'), 0, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('Enter amount')
        form_layout.addWidget(self.amount_input, 0, 1)
        
        # Category input
        form_layout.addWidget(QLabel('Category:'), 1, 0)
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText('e.g., Groceries, Rent, etc.')
        form_layout.addWidget(self.category_input, 1, 1)
        
        # Transaction type selection
        form_layout.addWidget(QLabel('Type:'), 2, 0)
        self.type_select = QComboBox()
        self.type_select.addItems(['expense', 'income'])
        form_layout.addWidget(self.type_select, 2, 1)
        
        # Description input
        form_layout.addWidget(QLabel('Description:'), 3, 0)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText('Enter description')
        form_layout.addWidget(self.description_input, 3, 1)
        
        # Date selection
        form_layout.addWidget(QLabel('Date:'), 4, 0)
        self.date_select = QDateEdit()
        self.date_select.setDate(QDate.currentDate())
        self.date_select.setCalendarPopup(True)
        form_layout.addWidget(self.date_select, 4, 1)
        
        # Add transaction button
        add_btn = QPushButton('Add Transaction')
        add_btn.clicked.connect(self.add_transaction)
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        form_layout.addWidget(add_btn, 5, 0, 1, 2)
        
        left_panel.addWidget(form_frame)
        
        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(5)
        self.transaction_table.setHorizontalHeaderLabels(['Date', 'Category', 'Type', 'Amount', 'Description'])
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transaction_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #ddd;
            }
        """)
        left_panel.addWidget(self.transaction_table)
        
        content.addLayout(left_panel)
        
        # Right side - Charts
        right_panel = QVBoxLayout()
        
        # Transaction overview chart
        chart_frame = QFrame()
        chart_frame.setFrameStyle(QFrame.StyledPanel)
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        right_panel.addWidget(chart_frame)
        content.addLayout(right_panel)
        
        # Add content to main layout
        layout.addLayout(content)
        
    def add_transaction(self):
        """Add a new transaction."""
        try:
            amount = float(self.amount_input.text())
            category = self.category_input.text()
            transaction_type = self.type_select.currentText()
            description = self.description_input.text()
            date = self.date_select.date().toPyDate()
            
            if not all([amount > 0, category, transaction_type]):
                self.main_window.show_error('Please fill in all required fields')
                return
                
            transaction = self.main_window.app.add_transaction(
                amount=amount,
                category=category,
                transaction_type=transaction_type,
                description=description,
                date=date
            )
            
            self.main_window.show_success('Transaction added successfully')
            self.clear_inputs()
            self.refresh_data()
            
        except ValueError as e:
            self.main_window.show_error(str(e))
        except Exception as e:
            self.main_window.show_error(f'Error adding transaction: {str(e)}')
            
    def clear_inputs(self):
        """Clear form inputs."""
        self.amount_input.clear()
        self.category_input.clear()
        self.description_input.clear()
        self.date_select.setDate(QDate.currentDate())
        self.type_select.setCurrentIndex(0)
        
    def refresh_data(self):
        """Refresh transaction data and charts."""
        try:
            # Get transaction data
            transactions = self.main_window.app.get_transactions()
            
            # Update transaction table
            self.transaction_table.setRowCount(0)
            for transaction in transactions:
                row = self.transaction_table.rowCount()
                self.transaction_table.insertRow(row)
                
                self.transaction_table.setItem(row, 0, QTableWidgetItem(transaction['date'].strftime('%Y-%m-%d')))
                self.transaction_table.setItem(row, 1, QTableWidgetItem(transaction['category']))
                self.transaction_table.setItem(row, 2, QTableWidgetItem(transaction['type']))
                amount_str = self.main_window.app.format_amount(transaction['amount'])
                self.transaction_table.setItem(row, 3, QTableWidgetItem(amount_str))
                self.transaction_table.setItem(row, 4, QTableWidgetItem(transaction.get('description', '')))
                
            # Update charts
            self.ax1.clear()
            self.ax2.clear()
            
            # Expenses by category pie chart
            expenses = {}
            for t in transactions:
                if t['type'] == 'expense':
                    expenses[t['category']] = expenses.get(t['category'], 0) + t['amount']
                    
            if expenses:
                self.ax1.pie(expenses.values(), labels=expenses.keys(), autopct='%1.1f%%')
                self.ax1.set_title('Expenses by Category')
            
            # Income vs Expenses bar chart
            income = sum(t['amount'] for t in transactions if t['type'] == 'income')
            total_expenses = sum(expenses.values())
            
            self.ax2.bar(['Income', 'Expenses'], [income, total_expenses], color=['#4CAF50', '#f44336'])
            self.ax2.set_title('Income vs Expenses')
            self.ax2.set_ylabel('Amount ($)')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.main_window.show_error(f'Error refreshing transaction data: {str(e)}')
