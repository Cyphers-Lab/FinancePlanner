"""Investment management page for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QGridLayout, QLineEdit,
                           QComboBox, QTableWidget, QTableWidgetItem,
                           QHeaderView, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

class InvestmentPage(QWidget):
    """Investment page for managing investment portfolio."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel('Investment Portfolio')
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
        
        # Left side - Investment Form and Table
        left_panel = QVBoxLayout()
        
        # Investment creation form
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
        
        # Investment type selection
        form_layout.addWidget(QLabel('Type:'), 0, 0)
        self.type_select = QComboBox()
        self.type_select.addItems(['STOCK', 'CRYPTO', 'ETF', 'MUTUAL_FUND', 'BOND', 'VANGUARD_FUND'])
        self.type_select.currentTextChanged.connect(self.on_type_changed)
        form_layout.addWidget(self.type_select, 0, 1)
        
        # Symbol input
        form_layout.addWidget(QLabel('Symbol:'), 1, 0)
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText('e.g., AAPL, BTC, VANGXXXX')
        form_layout.addWidget(self.symbol_input, 1, 1)
        
        # Quantity input
        form_layout.addWidget(QLabel('Quantity:'), 2, 0)
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText('Enter quantity')
        form_layout.addWidget(self.quantity_input, 2, 1)
        
        # Purchase price input
        form_layout.addWidget(QLabel('Purchase Price:'), 3, 0)
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText('Enter price per unit')
        form_layout.addWidget(self.price_input, 3, 1)
        
        # Currency selection
        form_layout.addWidget(QLabel('Currency:'), 4, 0)
        self.currency_select = QComboBox()
        self.currency_select.addItems(['USD', 'EUR', 'GBP', 'JPY', 'CHF'])
        form_layout.addWidget(self.currency_select, 4, 1)
        
        # Add investment button
        add_btn = QPushButton('Add Investment')
        add_btn.clicked.connect(self.add_investment)
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
        
        # Portfolio table
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(7)
        self.portfolio_table.setHorizontalHeaderLabels([
            'Type', 'Symbol', 'Quantity', 'Purchase Price', 
            'Current Price', 'Gain/Loss', 'Currency'
        ])
        self.portfolio_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.portfolio_table.setStyleSheet("""
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
        left_panel.addWidget(self.portfolio_table)
        
        content.addLayout(left_panel)
        
        # Right side - Charts
        right_panel = QVBoxLayout()
        
        # Portfolio overview chart
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
        
    def on_type_changed(self, investment_type):
        """Handle investment type changes."""
        if investment_type == 'VANGUARD_FUND':
            self.symbol_input.setPlaceholderText('Enter Vanguard symbol (e.g., VANGXXXX, VUAG)')
        else:
            self.symbol_input.setPlaceholderText('e.g., AAPL, BTC, etc.')

    def add_investment(self):
        """Add a new investment."""
        try:
            investment_type = self.type_select.currentText()
            symbol = self.symbol_input.text().upper()
            quantity = float(self.quantity_input.text())
            purchase_price = float(self.price_input.text())
            
            if not all([symbol, quantity > 0, purchase_price > 0]):
                self.main_window.show_error('Please fill in all fields with valid values')
                return
                
            if investment_type == 'VANGUARD_FUND' and not (symbol.upper().startswith('VANG') or symbol.upper().startswith('VU')):
                self.main_window.show_error('Vanguard symbols must start with VANG or VU')
                return
                
            currency = self.currency_select.currentText()
            investment = self.main_window.app.add_investment(
                investment_type=investment_type,
                symbol=symbol,
                quantity=quantity,
                purchase_price=purchase_price,
                currency=currency
            )
            
            self.main_window.show_success('Investment added successfully')
            self.clear_inputs()
            self.refresh_data()
            
        except ValueError as e:
            self.main_window.show_error(str(e))
        except Exception as e:
            self.main_window.show_error(f'Error adding investment: {str(e)}')
            
    def clear_inputs(self):
        """Clear form inputs."""
        self.symbol_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.type_select.setCurrentIndex(0)
        
    def update_price(self, row):
        """Open dialog to update investment price."""
        investment = self.main_window.app.get_portfolio_summary()['investments'][row]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Update Price - {investment['symbol']}")
        
        layout = QVBoxLayout(dialog)
        
        # Price input
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel('Current Price:'))
        price_input = QLineEdit()
        price_input.setPlaceholderText('Enter new price')
        price_layout.addWidget(price_input)
        layout.addLayout(price_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                new_price = float(price_input.text())
                if new_price <= 0:
                    raise ValueError("Price must be greater than 0")
                    
                self.main_window.app.update_investment_price(
                    investment_id=investment['id'],
                    current_price=new_price
                )
                self.refresh_data()
                self.main_window.show_success('Price updated successfully')
            except ValueError as e:
                self.main_window.show_error(str(e))
            except Exception as e:
                self.main_window.show_error(f'Error updating price: {str(e)}')

    def refresh_data(self):
        """Refresh investment data and charts."""
        try:
            # Get portfolio data
            portfolio_data = self.main_window.app.get_portfolio_summary()
            
            # Update portfolio table
            self.portfolio_table.setRowCount(0)
            for investment in portfolio_data.get('investments', []):
                row = self.portfolio_table.rowCount()
                self.portfolio_table.insertRow(row)
                
                # Format the investment type display
                display_type = investment['type']
                if display_type == 'VANGUARD_FUND':
                    display_type = 'Vanguard Fund'
                elif display_type == 'MUTUAL_FUND':
                    display_type = 'Mutual Fund'
                elif display_type == 'ETF':
                    display_type = 'ETF'
                self.portfolio_table.setItem(row, 0, QTableWidgetItem(display_type))
                self.portfolio_table.setItem(row, 1, QTableWidgetItem(investment['symbol']))
                self.portfolio_table.setItem(row, 2, QTableWidgetItem(f"{investment['quantity']:.4f}"))
                currency_symbol = {
                    'USD': '$', 'EUR': '€', 'GBP': '£',
                    'JPY': '¥', 'CHF': 'Fr.'
                }.get(investment['currency'], '$')
                
                self.portfolio_table.setItem(row, 3, QTableWidgetItem(
                    f"{currency_symbol}{investment['purchase_price']:.2f}"
                ))
                # Current price with update button
                price_cell = QWidget()
                price_layout = QHBoxLayout(price_cell)
                price_layout.setContentsMargins(5, 0, 5, 0)
                
                currency_symbol = {
                    'USD': '$', 'EUR': '€', 'GBP': '£',
                    'JPY': '¥', 'CHF': 'Fr.'
                }.get(investment['currency'], '$')
                
                price_label = QLabel(f"{currency_symbol}{investment['current_price']:.2f}")
                price_layout.addWidget(price_label)
                
                update_btn = QPushButton("Update")
                update_btn.setStyleSheet("""
                    QPushButton {
                        padding: 2px 8px;
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 2px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                update_btn.clicked.connect(lambda checked, r=row: self.update_price(r))
                price_layout.addWidget(update_btn)
                
                self.portfolio_table.setCellWidget(row, 4, price_cell)
                
                gain_loss = (investment['current_price'] - investment['purchase_price']) * investment['quantity']
                gain_loss_text = f"{currency_symbol}{gain_loss:.2f}"
                gain_loss_item = QTableWidgetItem(gain_loss_text)
                gain_loss_item.setForeground(Qt.green if gain_loss >= 0 else Qt.red)
                self.portfolio_table.setItem(row, 5, gain_loss_item)
                self.portfolio_table.setItem(row, 6, QTableWidgetItem(investment['currency']))
                
            # Update charts
            self.ax1.clear()
            self.ax2.clear()
            
            # Portfolio allocation pie chart
            allocations = {}
            for inv in portfolio_data.get('investments', []):
                value = inv['quantity'] * inv['current_price']
                allocations[inv['symbol']] = value
                
            if allocations:
                self.ax1.pie(allocations.values(), labels=allocations.keys(), autopct='%1.1f%%')
                self.ax1.set_title('Portfolio Allocation')
            
            # Performance bar chart
            symbols = [inv['symbol'] for inv in portfolio_data.get('investments', [])]
            returns = [(inv['current_price'] - inv['purchase_price']) / inv['purchase_price'] * 100
                      for inv in portfolio_data.get('investments', [])]
            
            if symbols and returns:
                bars = self.ax2.bar(symbols, returns)
                self.ax2.set_title('Investment Returns (%)')
                self.ax2.set_ylabel('Return (%)')
                
                # Color bars based on performance
                for bar, ret in zip(bars, returns):
                    bar.set_color('#4CAF50' if ret >= 0 else '#f44336')
                
                # Rotate x-axis labels for better readability
                plt.setp(self.ax2.get_xticklabels(), rotation=45, ha='right')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.main_window.show_error(f'Error refreshing investment data: {str(e)}')
