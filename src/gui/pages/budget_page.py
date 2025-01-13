"""Budget management page for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QScrollArea, QGridLayout,
                           QLineEdit, QComboBox, QDateEdit, QTableWidget,
                           QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

class BudgetPage(QWidget):
    """Budget page for creating and managing budgets."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel('Budget Management')
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
        
        # Left side - Budget Form and Table
        left_panel = QVBoxLayout()
        
        # Budget creation form
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
        
        # Category input
        form_layout.addWidget(QLabel('Category:'), 0, 0)
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText('e.g., Groceries, Rent, etc.')
        form_layout.addWidget(self.category_input, 0, 1)
        
        # Amount input
        form_layout.addWidget(QLabel('Amount:'), 1, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('Enter amount')
        form_layout.addWidget(self.amount_input, 1, 1)
        
        # Month selection
        form_layout.addWidget(QLabel('Month:'), 2, 0)
        self.month_select = QDateEdit()
        self.month_select.setDisplayFormat('MMMM yyyy')
        self.month_select.setDate(QDate.currentDate())
        form_layout.addWidget(self.month_select, 2, 1)
        
        # Add budget button
        add_btn = QPushButton('Add Budget')
        add_btn.clicked.connect(self.add_budget)
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
        form_layout.addWidget(add_btn, 3, 0, 1, 2)
        
        left_panel.addWidget(form_frame)
        
        # Budget table
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(4)
        self.budget_table.setHorizontalHeaderLabels(['Category', 'Budget', 'Spent', 'Remaining'])
        self.budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.budget_table.setStyleSheet("""
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
        left_panel.addWidget(self.budget_table)
        
        content.addLayout(left_panel)
        
        # Right side - Charts
        right_panel = QVBoxLayout()
        
        # Budget overview chart
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
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        right_panel.addWidget(chart_frame)
        content.addLayout(right_panel)
        
        # Add content to main layout
        layout.addLayout(content)
        
    def add_budget(self):
        """Add a new budget category."""
        try:
            category = self.category_input.text()
            amount = float(self.amount_input.text())
            month = self.month_select.date().toPyDate()
            
            if not category or amount <= 0:
                self.main_window.show_error('Please enter valid category and amount')
                return
                
            budget = self.main_window.app.create_budget(category, amount, month)
            self.main_window.show_success('Budget created successfully')
            self.clear_inputs()
            self.refresh_data()
            
        except ValueError as e:
            self.main_window.show_error(str(e))
        except Exception as e:
            self.main_window.show_error(f'Error creating budget: {str(e)}')
            
    def clear_inputs(self):
        """Clear form inputs."""
        self.category_input.clear()
        self.amount_input.clear()
        self.month_select.setDate(QDate.currentDate())
        
    def refresh_data(self):
        """Refresh budget data and charts."""
        try:
            # Get budget summary
            budget_data = self.main_window.app.get_budget_summary(datetime.now())
            
            # Update table
            self.budget_table.setRowCount(0)
            for category_data in budget_data['categories']:
                row = self.budget_table.rowCount()
                self.budget_table.insertRow(row)
                self.budget_table.setItem(row, 0, QTableWidgetItem(category_data['category']))
                self.budget_table.setItem(row, 1, QTableWidgetItem(f"${category_data['budgeted']:.2f}"))
                self.budget_table.setItem(row, 2, QTableWidgetItem(f"${category_data['spent']:.2f}"))
                self.budget_table.setItem(row, 3, QTableWidgetItem(f"${category_data['remaining']:.2f}"))
                
            # Update chart
            self.ax.clear()
            categories = [data['category'] for data in budget_data['categories']]
            budgets = [data['budgeted'] for data in budget_data['categories']]
            spent = [data['spent'] for data in budget_data['categories']]
            
            x = range(len(categories))
            width = 0.35
            
            self.ax.bar([i - width/2 for i in x], budgets, width, label='Budget', color='#2196F3')
            self.ax.bar([i + width/2 for i in x], spent, width, label='Spent', color='#4CAF50')
            
            self.ax.set_ylabel('Amount ($)')
            self.ax.set_title('Budget vs Spending by Category')
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(categories, rotation=45, ha='right')
            self.ax.legend()
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.main_window.show_error(f'Error refreshing budget data: {str(e)}')
