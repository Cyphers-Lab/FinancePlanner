"""Cash flow forecasting page for the Financial Planner application."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QSpinBox, QTreeWidget,
                           QTreeWidgetItem, QSplitter, QFrame, QLineEdit,
                           QTextEdit, QMessageBox, QDialog, QFormLayout,
                           QDialogButtonBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import json
from datetime import datetime, timedelta

from ...models.models import TransactionType, RecurringFrequency, ForecastType, RecurringTransaction
from ...services.forecast_service import ForecastService

class ForecastPage(QWidget):
    """Page for cash flow forecasting and analysis."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.forecast_service = None
        self.current_forecast = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Control panel
        # Header with navigation
        header = QHBoxLayout()
        title = QLabel('Cash Flow Forecast')
        title.setStyleSheet('font-size: 24px; font-weight: bold;')
        header.addWidget(title)
        
        # Navigation buttons
        nav_buttons = QHBoxLayout()
        nav_buttons.setAlignment(Qt.AlignRight)
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.clicked.connect(self.main_window.show_dashboard)
        nav_buttons.addWidget(back_btn)
        
        header.addLayout(nav_buttons)
        layout.addLayout(header)
        
        # Control panel
        control_panel = QHBoxLayout()
        
        # Forecast type combo
        self.forecast_type_combo = QComboBox()
        for forecast_type in ForecastType:
            self.forecast_type_combo.addItem(forecast_type.value)
        control_panel.addWidget(QLabel("Forecast Type:"))
        control_panel.addWidget(self.forecast_type_combo)
        
        # Periods spinbox
        self.periods_spin = QSpinBox()
        self.periods_spin.setRange(1, 24)
        self.periods_spin.setValue(12)
        control_panel.addWidget(QLabel("Periods:"))
        control_panel.addWidget(self.periods_spin)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Forecast")
        refresh_btn.clicked.connect(self.refresh_data)
        control_panel.addWidget(refresh_btn)
        
        control_panel.addStretch()
        layout.addLayout(control_panel)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Recurring Transactions
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("Recurring Transactions"))
        
        # Recurring transactions tree
        self.recurring_tree = QTreeWidget()
        self.recurring_tree.setHeaderLabels([
            "Name", "Type", "Amount", "Frequency", "Next Due"
        ])
        self.recurring_tree.setColumnWidth(0, 150)
        left_layout.addWidget(self.recurring_tree)
        
        # Transaction buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Recurring")
        add_btn.clicked.connect(self.show_add_recurring_dialog)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.show_edit_recurring_dialog)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_recurring)
        btn_layout.addWidget(delete_btn)
        
        detect_btn = QPushButton("Detect Patterns")
        detect_btn.clicked.connect(self.show_detect_patterns_dialog)
        btn_layout.addWidget(detect_btn)
        
        left_layout.addLayout(btn_layout)
        
        splitter.addWidget(left_widget)
        
        # Right side - Forecast Visualization
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("Cash Flow Forecast"))
        
        # Matplotlib figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)
        
        # What-if analysis
        whatif_frame = QFrame()
        whatif_frame.setFrameStyle(QFrame.StyledPanel)
        whatif_layout = QHBoxLayout(whatif_frame)
        
        whatif_layout.addWidget(QLabel("Add hypothetical:"))
        
        self.whatif_amount = QLineEdit()
        self.whatif_amount.setPlaceholderText("Amount")
        whatif_layout.addWidget(self.whatif_amount)
        
        self.whatif_type = QComboBox()
        self.whatif_type.addItems([
            TransactionType.INCOME.value,
            TransactionType.EXPENSE.value
        ])
        whatif_layout.addWidget(self.whatif_type)
        
        self.whatif_date = QDateEdit()
        self.whatif_date.setDate(
            QDate.currentDate().addDays(30)
        )
        whatif_layout.addWidget(self.whatif_date)
        
        simulate_btn = QPushButton("Simulate")
        simulate_btn.clicked.connect(self.simulate_whatif)
        whatif_layout.addWidget(simulate_btn)
        
        right_layout.addWidget(whatif_frame)
        
        # Insights
        right_layout.addWidget(QLabel("Insights"))
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setMaximumHeight(100)
        right_layout.addWidget(self.insights_text)
        
        splitter.addWidget(right_widget)
        
        layout.addWidget(splitter)
    
    def refresh_data(self):
        """Refresh all data on the page."""
        try:
            if not self.main_window.app.current_user:
                self.recurring_tree.clear()
                self.insights_text.setPlainText("Please log in to view forecasts")
                return
                
            if not self.forecast_service:
                self.forecast_service = ForecastService(self.main_window.app.db)
            
            self.refresh_recurring_transactions()
            self.refresh_forecast()
            
        except Exception as e:
            self.main_window.show_error(f"Error refreshing forecast data: {str(e)}")
    
    def refresh_recurring_transactions(self):
        """Refresh the recurring transactions list."""
        self.recurring_tree.clear()
        
        recurring_txs = self.forecast_service.db.query(RecurringTransaction).filter(
            RecurringTransaction.user_id == self.main_window.app.current_user.id
        ).all()
        
        for tx in recurring_txs:
            item = QTreeWidgetItem([
                tx.name,
                tx.type.value,
                f"${tx.amount:.2f}",
                tx.frequency.value,
                tx.next_occurrence.strftime('%Y-%m-%d')
            ])
            self.recurring_tree.addTopLevelItem(item)
    
    def refresh_forecast(self):
        """Generate and display a new forecast."""
        self.current_forecast = self.forecast_service.generate_forecast(
            self.main_window.app.current_user.id,
            ForecastType(self.forecast_type_combo.currentText()),
            periods=self.periods_spin.value()
        )
        
        self.update_visualization()
        self.update_insights()
    
    def update_visualization(self):
        """Update the forecast visualization."""
        if not self.current_forecast:
            return
            
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        dates = []
        net_flows = []
        running_balance = 0
        balances = []
        
        for period in self.current_forecast.forecast_data:
            dates.append(datetime.fromisoformat(period['start_date']))
            net_flow = period['net_cash_flow']
            net_flows.append(net_flow)
            running_balance += net_flow
            balances.append(running_balance)
        
        ax.bar(dates, net_flows, alpha=0.3, label='Net Cash Flow')
        
        ax2 = ax.twinx()
        ax2.plot(dates, balances, color='red', label='Running Balance')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Net Cash Flow ($)')
        ax2.set_ylabel('Running Balance ($)')
        
        for label in ax.xaxis.get_ticklabels():
            label.set_rotation(45)
        
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_insights(self):
        """Update forecast insights."""
        if not self.current_forecast:
            return
            
        insights = []
        total_income = 0
        total_expense = 0
        lowest_balance = float('inf')
        highest_balance = float('-inf')
        running_balance = 0
        
        for period in self.current_forecast.forecast_data:
            running_balance += period['net_cash_flow']
            lowest_balance = min(lowest_balance, running_balance)
            highest_balance = max(highest_balance, running_balance)
            
            for tx in period['transactions']:
                if tx['type'] == TransactionType.INCOME.value:
                    total_income += tx['amount']
                else:
                    total_expense += tx['amount']
        
        if lowest_balance < 0:
            insights.append(
                f"⚠️ Potential cash flow shortage detected! Lowest balance: ${lowest_balance:.2f}"
            )
        
        savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
        insights.append(f"Projected savings rate: {savings_rate:.1f}%")
        
        if highest_balance > total_expense * 3:
            insights.append(
                "💡 Consider investing excess cash to maximize returns"
            )
        
        self.insights_text.setPlainText('\n'.join(insights))
    
    def show_add_recurring_dialog(self):
        """Show dialog to add a new recurring transaction."""
        if not self.main_window.app.current_user:
            self.main_window.show_error("Please log in to add recurring transactions")
            return
            
        dialog = RecurringTransactionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()
    
    def show_edit_recurring_dialog(self):
        """Show dialog to edit selected recurring transaction."""
        if not self.main_window.app.current_user:
            self.main_window.show_error("Please log in to edit recurring transactions")
            return
            
        selected = self.recurring_tree.selectedItems()
        if not selected:
            return
            
        item = selected[0]
        dialog = RecurringTransactionDialog(
            self,
            edit_mode=True,
            initial_values={
                'name': item.text(0),
                'type': item.text(1),
                'amount': float(item.text(2).replace('$', '')),
                'frequency': item.text(3)
            }
        )
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()
    
    def delete_recurring(self):
        """Delete selected recurring transaction."""
        if not self.main_window.app.current_user:
            self.main_window.show_error("Please log in to delete recurring transactions")
            return
            
        selected = self.recurring_tree.selectedItems()
        if not selected:
            return
            
        item = selected[0]
        tx = self.forecast_service.db.query(RecurringTransaction).filter(
            RecurringTransaction.user_id == self.main_window.app.current_user.id,
            RecurringTransaction.name == item.text(0)
        ).first()
        
        if tx:
            self.forecast_service.db.delete(tx)
            self.forecast_service.db.commit()
            self.refresh_data()
    
    def show_detect_patterns_dialog(self):
        """Show dialog with detected transaction patterns."""
        if not self.main_window.app.current_user:
            self.main_window.show_error("Please log in to detect transaction patterns")
            return
            
        patterns = self.forecast_service.detect_recurring_transactions(
            self.main_window.app.current_user.id
        )
        dialog = DetectedPatternsDialog(self, patterns)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()
    
    def simulate_whatif(self):
        """Simulate adding a hypothetical transaction to the forecast."""
        if not self.main_window.app.current_user:
            self.main_window.show_error("Please log in to use what-if analysis")
            return
            
        try:
            amount = float(self.whatif_amount.text())
            date = self.whatif_date.date().toPyDate()
            tx_type = TransactionType(self.whatif_type.currentText())
            
            forecast_data = json.loads(json.dumps(self.current_forecast.forecast_data))
            
            for period in forecast_data:
                start = datetime.fromisoformat(period['start_date'])
                end = datetime.fromisoformat(period['end_date'])
                
                if start <= date < end:
                    period['transactions'].append({
                        'date': date.isoformat(),
                        'name': 'Hypothetical Transaction',
                        'type': tx_type.value,
                        'amount': amount,
                        'category': 'What-if'
                    })
                    
                    period['net_cash_flow'] += amount if tx_type == TransactionType.INCOME else -amount
                    break
            
            self.current_forecast.forecast_data = forecast_data
            self.update_visualization()
            self.update_insights()
            
        except ValueError:
            QMessageBox.critical(
                self,
                "Error",
                "Invalid amount. Please enter a valid number."
            )

class RecurringTransactionDialog(QDialog):
    """Dialog for adding/editing recurring transactions."""
    
    def __init__(
        self, parent, edit_mode: bool = False,
        initial_values: dict = None
    ):
        super().__init__(parent)
        self.parent = parent
        self.edit_mode = edit_mode
        
        self.setWindowTitle(
            "Edit Recurring Transaction" if edit_mode else "Add Recurring Transaction"
        )
        self.setModal(True)
        
        self.init_ui(initial_values or {})
    
    def init_ui(self, initial_values: dict):
        """Initialize the dialog UI."""
        layout = QFormLayout(self)
        
        # Name
        self.name_edit = QLineEdit(initial_values.get('name', ''))
        layout.addRow("Name:", self.name_edit)
        
        # Type
        self.type_combo = QComboBox()
        for tx_type in TransactionType:
            self.type_combo.addItem(tx_type.value)
        if 'type' in initial_values:
            self.type_combo.setCurrentText(initial_values['type'])
        layout.addRow("Type:", self.type_combo)
        
        # Amount
        self.amount_edit = QLineEdit(str(initial_values.get('amount', '')))
        layout.addRow("Amount:", self.amount_edit)
        
        # Category
        self.category_edit = QLineEdit(initial_values.get('category', ''))
        layout.addRow("Category:", self.category_edit)
        
        # Frequency
        self.frequency_combo = QComboBox()
        for freq in RecurringFrequency:
            self.frequency_combo.addItem(freq.value)
        if 'frequency' in initial_values:
            self.frequency_combo.setCurrentText(initial_values['frequency'])
        layout.addRow("Frequency:", self.frequency_combo)
        
        # Start Date
        self.start_date = QDateEdit(QDate.currentDate())
        layout.addRow("Start Date:", self.start_date)
        
        # End Date (optional)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setSpecialValueText("No End Date")
        layout.addRow("End Date (optional):", self.end_date)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def accept(self):
        """Validate and save the recurring transaction."""
        try:
            name = self.name_edit.text().strip()
            if not name:
                raise ValueError("Name is required")
                
            amount = float(self.amount_edit.text())
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            category = self.category_edit.text().strip()
            if not category:
                raise ValueError("Category is required")
                
            start_date = self.start_date.date().toPyDate()
            
            end_date = None
            if not self.end_date.specialValueText():
                end_date = self.end_date.date().toPyDate()
                if end_date <= start_date:
                    raise ValueError("End date must be after start date")
            
            self.parent.forecast_service.create_recurring_transaction(
                user_id=self.parent.main_window.app.current_user.id,
                name=name,
                tx_type=TransactionType(self.type_combo.currentText()),
                amount=amount,
                category=category,
                frequency=RecurringFrequency(self.frequency_combo.currentText()),
                start_date=start_date,
                end_date=end_date
            )
            
            super().accept()
            
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

class DetectedPatternsDialog(QDialog):
    """Dialog for displaying and selecting detected transaction patterns."""
    
    def __init__(self, parent, patterns):
        super().__init__(parent)
        self.parent = parent
        self.patterns = patterns
        
        self.setWindowTitle("Detected Transaction Patterns")
        self.setModal(True)
        self.resize(600, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Patterns tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            "Category", "Type", "Amount", "Frequency", "Confidence"
        ])
        layout.addWidget(self.tree)
        
        # Populate patterns
        for pattern in self.patterns:
            item = QTreeWidgetItem([
                pattern['category'],
                pattern['type'].value,
                f"${pattern['amount']:.2f}",
                pattern['frequency'].value,
                f"{pattern['confidence']*100:.1f}%"
            ])
            self.tree.addTopLevelItem(item)
        
        # Buttons
        button_box = QDialogButtonBox()
        add_btn = button_box.addButton("Add Selected", QDialogButtonBox.ActionRole)
        add_btn.clicked.connect(self.add_selected)
        button_box.addButton(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def add_selected(self):
        """Add selected patterns as recurring transactions."""
        selected = self.tree.selectedItems()
        if not selected:
            return
            
        for item in selected:
            self.parent.forecast_service.create_recurring_transaction(
                user_id=self.parent.main_window.app.current_user.id,
                name=f"Auto-detected: {item.text(0)}",
                tx_type=TransactionType(item.text(1)),
                amount=float(item.text(2).replace('$', '')),
                category=item.text(0),
                frequency=RecurringFrequency(item.text(3)),
                start_date=datetime.now()
            )
        
        self.accept()
