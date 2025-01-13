"""Debt management page for the Financial Planner GUI."""
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

class DebtPage(QWidget):
    """Debt page for managing debts and payment strategies."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel('Debt Management')
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
        
        # Left side - Debt Form and Table
        left_panel = QVBoxLayout()
        
        # Debt creation form
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
        
        # Debt name input
        form_layout.addWidget(QLabel('Name:'), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('e.g., Credit Card, Student Loan, etc.')
        form_layout.addWidget(self.name_input, 0, 1)
        
        # Total amount input
        form_layout.addWidget(QLabel('Total Amount:'), 1, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('Enter total debt amount')
        form_layout.addWidget(self.amount_input, 1, 1)
        
        # Interest rate input
        form_layout.addWidget(QLabel('Interest Rate (%):'), 2, 0)
        self.interest_input = QLineEdit()
        self.interest_input.setPlaceholderText('Enter annual interest rate')
        form_layout.addWidget(self.interest_input, 2, 1)
        
        # Minimum payment input
        form_layout.addWidget(QLabel('Minimum Payment:'), 3, 0)
        self.min_payment_input = QLineEdit()
        self.min_payment_input.setPlaceholderText('Enter minimum monthly payment')
        form_layout.addWidget(self.min_payment_input, 3, 1)
        
        # Due date selection
        form_layout.addWidget(QLabel('Due Date:'), 4, 0)
        self.due_date_select = QDateEdit()
        self.due_date_select.setDate(QDate.currentDate())
        self.due_date_select.setCalendarPopup(True)
        form_layout.addWidget(self.due_date_select, 4, 1)
        
        # Add debt button
        add_btn = QPushButton('Add Debt')
        add_btn.clicked.connect(self.add_debt)
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
        
        # Debt table
        self.debt_table = QTableWidget()
        self.debt_table.setColumnCount(6)
        self.debt_table.setHorizontalHeaderLabels([
            'Name', 'Total Amount', 'Remaining', 'Interest Rate', 
            'Minimum Payment', 'Due Date'
        ])
        self.debt_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.debt_table.setStyleSheet("""
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
        left_panel.addWidget(self.debt_table)
        
        content.addLayout(left_panel)
        
        # Right side - Payment Strategy and Charts
        right_panel = QVBoxLayout()
        
        # Payment strategy section
        strategy_frame = QFrame()
        strategy_frame.setFrameStyle(QFrame.StyledPanel)
        strategy_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        strategy_layout = QVBoxLayout(strategy_frame)
        
        strategy_header = QHBoxLayout()
        strategy_layout.addLayout(strategy_header)
        
        strategy_header.addWidget(QLabel('Payment Strategy'))
        
        # Strategy selection
        self.strategy_select = QComboBox()
        self.strategy_select.addItems(['Avalanche (Highest Interest First)', 'Snowball (Lowest Balance First)'])
        strategy_header.addWidget(self.strategy_select)
        
        # Monthly budget input
        self.budget_input = QLineEdit()
        self.budget_input.setPlaceholderText('Enter monthly debt payment budget')
        strategy_layout.addWidget(self.budget_input)
        
        # Calculate strategy button
        calc_btn = QPushButton('Calculate Strategy')
        calc_btn.clicked.connect(self.calculate_strategy)
        calc_btn.setStyleSheet("""
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
        strategy_layout.addWidget(calc_btn)
        
        # Strategy results
        self.strategy_results = QLabel('Enter your monthly budget to see payment recommendations')
        self.strategy_results.setWordWrap(True)
        strategy_layout.addWidget(self.strategy_results)
        
        right_panel.addWidget(strategy_frame)
        
        # Debt overview charts
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
        
    def add_debt(self):
        """Add a new debt."""
        try:
            name = self.name_input.text()
            total_amount = float(self.amount_input.text())
            interest_rate = float(self.interest_input.text())
            minimum_payment = float(self.min_payment_input.text())
            due_date = self.due_date_select.date().toPyDate()
            
            if not all([name, total_amount > 0, interest_rate >= 0, minimum_payment > 0]):
                self.main_window.show_error('Please fill in all fields with valid values')
                return
                
            debt = self.main_window.app.add_debt(
                name=name,
                total_amount=total_amount,
                interest_rate=interest_rate,
                minimum_payment=minimum_payment,
                due_date=due_date
            )
            
            self.main_window.show_success('Debt added successfully')
            self.clear_inputs()
            self.refresh_data()
            
        except ValueError as e:
            self.main_window.show_error(str(e))
        except Exception as e:
            self.main_window.show_error(f'Error adding debt: {str(e)}')
            
    def calculate_strategy(self):
        """Calculate and display debt payment strategy."""
        try:
            monthly_budget = float(self.budget_input.text())
            strategy = 'avalanche' if 'Avalanche' in self.strategy_select.currentText() else 'snowball'
            
            if monthly_budget <= 0:
                self.main_window.show_error('Please enter a valid monthly budget')
                return
                
            strategy_data = self.main_window.app.get_debt_payment_strategy(
                monthly_budget=monthly_budget,
                strategy=strategy
            )
            
            # Format and display strategy results
            result_text = f"<h3>Payment Strategy:</h3>"
            for payment in strategy_data:
                result_text += f"""
                    <p><b>{payment['name']}</b><br>
                    Suggested Payment: ${payment['suggested_payment']:.2f}<br>
                    (Minimum: ${payment['minimum_payment']:.2f})<br>
                    Remaining: ${payment['remaining_amount']:.2f}<br>
                    Interest Rate: {payment['interest_rate']:.1f}%</p>
                """
            
            self.strategy_results.setText(result_text)
            
        except ValueError as e:
            self.main_window.show_error(str(e))
        except Exception as e:
            self.main_window.show_error(f'Error calculating strategy: {str(e)}')
            
    def clear_inputs(self):
        """Clear form inputs."""
        self.name_input.clear()
        self.amount_input.clear()
        self.interest_input.clear()
        self.min_payment_input.clear()
        self.due_date_select.setDate(QDate.currentDate())
        
    def refresh_data(self):
        """Refresh debt data and charts."""
        try:
            # Get debt summary data
            debt_data = self.main_window.app.get_debt_summary()
            
            # Update debt table
            self.debt_table.setRowCount(0)
            for debt in debt_data['debts']:
                row = self.debt_table.rowCount()
                self.debt_table.insertRow(row)
                
                self.debt_table.setItem(row, 0, QTableWidgetItem(debt['name']))
                self.debt_table.setItem(row, 1, QTableWidgetItem(f"${debt['total']:.2f}"))
                self.debt_table.setItem(row, 2, QTableWidgetItem(f"${debt['remaining']:.2f}"))
                self.debt_table.setItem(row, 3, QTableWidgetItem(f"{debt['interest_rate']:.1f}%"))
                self.debt_table.setItem(row, 4, QTableWidgetItem(f"${debt['minimum_payment']:.2f}"))
                due_date = debt.get('due_date')
                due_date_str = due_date.strftime('%Y-%m-%d') if due_date else 'N/A'
                self.debt_table.setItem(row, 5, QTableWidgetItem(due_date_str))
                
            # Update charts
            self.ax1.clear()
            self.ax2.clear()
            
            # Debt distribution pie chart
            debt_amounts = {debt['name']: debt['remaining'] for debt in debt_data['debts']}
            if debt_amounts:
                self.ax1.pie(debt_amounts.values(), labels=debt_amounts.keys(), autopct='%1.1f%%')
                self.ax1.set_title('Debt Distribution')
            
            # Interest rates comparison
            names = [debt['name'] for debt in debt_data['debts']]
            rates = [debt['interest_rate'] for debt in debt_data['debts']]
            
            if names and rates:
                bars = self.ax2.bar(names, rates)
                self.ax2.set_title('Interest Rates by Debt')
                self.ax2.set_ylabel('Interest Rate (%)')
                
                # Rotate x-axis labels for better readability
                plt.setp(self.ax2.get_xticklabels(), rotation=45, ha='right')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.main_window.show_error(f'Error refreshing debt data: {str(e)}')
