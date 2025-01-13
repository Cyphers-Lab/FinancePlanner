"""Settings dialog for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QCheckBox, QGroupBox,
                           QSpinBox, QDoubleSpinBox, QFormLayout, QTabWidget,
                           QWidget)

class SettingsDialog(QDialog):
    """Dialog for changing user settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
        # Set current currency
        if self.parent.app.current_user:
            current_currency = self.parent.app.current_user.currency
            index = self.currency_select.findText(current_currency)
            if index >= 0:
                self.currency_select.setCurrentIndex(index)
            
            # Load user preferences
            self.load_preferences()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Settings')
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Currency selection
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel('Currency:'))
        self.currency_select = QComboBox()
        self.currency_select.addItems(['$', '£', '€', '¥'])
        currency_layout.addWidget(self.currency_select)
        general_layout.addLayout(currency_layout)
        
        tabs.addTab(general_tab, "General")
        
        # Insights tab
        insights_tab = QWidget()
        insights_layout = QVBoxLayout(insights_tab)
        
        # Alert thresholds
        thresholds_group = QGroupBox("Alert Thresholds")
        thresholds_layout = QFormLayout()
        
        self.spending_threshold = QDoubleSpinBox()
        self.spending_threshold.setRange(0.1, 1.0)
        self.spending_threshold.setSingleStep(0.1)
        self.spending_threshold.setDecimals(2)
        thresholds_layout.addRow("Spending Alert (% of budget):", self.spending_threshold)
        
        self.savings_threshold = QDoubleSpinBox()
        self.savings_threshold.setRange(0.1, 1.0)
        self.savings_threshold.setSingleStep(0.1)
        self.savings_threshold.setDecimals(2)
        thresholds_layout.addRow("Savings Alert (% of income):", self.savings_threshold)
        
        self.debt_threshold = QDoubleSpinBox()
        self.debt_threshold.setRange(0.1, 1.0)
        self.debt_threshold.setSingleStep(0.1)
        self.debt_threshold.setDecimals(2)
        thresholds_layout.addRow("Debt Alert (% of income):", self.debt_threshold)
        
        thresholds_group.setLayout(thresholds_layout)
        insights_layout.addWidget(thresholds_group)
        
        # Insight preferences
        preferences_group = QGroupBox("Insight Types")
        preferences_layout = QVBoxLayout()
        
        self.insight_checkboxes = {}
        insight_types = [
            ('spending_patterns', 'Spending Patterns'),
            ('savings_opportunities', 'Savings Opportunities'),
            ('investment_suggestions', 'Investment Suggestions'),
            ('budget_alerts', 'Budget Alerts'),
            ('debt_management', 'Debt Management')
        ]
        
        for key, label in insight_types:
            checkbox = QCheckBox(label)
            self.insight_checkboxes[key] = checkbox
            preferences_layout.addWidget(checkbox)
            
        preferences_group.setLayout(preferences_layout)
        insights_layout.addWidget(preferences_group)
        
        # Notification frequency
        frequency_layout = QHBoxLayout()
        frequency_layout.addWidget(QLabel('Notification Frequency:'))
        self.frequency_select = QComboBox()
        self.frequency_select.addItems(['daily', 'weekly', 'monthly'])
        frequency_layout.addWidget(self.frequency_select)
        insights_layout.addLayout(frequency_layout)
        
        # Risk tolerance
        risk_layout = QHBoxLayout()
        risk_layout.addWidget(QLabel('Risk Tolerance:'))
        self.risk_select = QComboBox()
        self.risk_select.addItems(['conservative', 'moderate', 'aggressive'])
        risk_layout.addWidget(self.risk_select)
        insights_layout.addLayout(risk_layout)
        
        tabs.addTab(insights_tab, "Insights")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Style the dialog
        self.style_widgets()
        
    def style_widgets(self):
        """Apply styles to widgets."""
        button_style = """
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
        """
        
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)
            
    def load_preferences(self):
        """Load current user preferences."""
        try:
            preferences = self.parent.app.get_user_preferences()
            
            # Set alert thresholds
            self.spending_threshold.setValue(preferences['alert_thresholds']['spending_alerts'])
            self.savings_threshold.setValue(preferences['alert_thresholds']['savings_alerts'])
            self.debt_threshold.setValue(preferences['alert_thresholds']['debt_alerts'])
            
            # Set insight preferences
            for key, checkbox in self.insight_checkboxes.items():
                checkbox.setChecked(preferences['insight_preferences'].get(key, True))
            
            # Set notification frequency
            index = self.frequency_select.findText(preferences['notification_frequency'])
            if index >= 0:
                self.frequency_select.setCurrentIndex(index)
            
            # Set risk tolerance
            index = self.risk_select.findText(preferences['risk_tolerance'])
            if index >= 0:
                self.risk_select.setCurrentIndex(index)
                
        except Exception as e:
            self.parent.show_error(f'Error loading preferences: {str(e)}')

    def save_settings(self):
        """Save the selected settings."""
        try:
            # Save currency
            currency = self.currency_select.currentText()
            if not self.parent.app.update_currency(currency):
                self.parent.show_error('Failed to update currency')
                return
            
            # Save preferences
            alert_thresholds = {
                'spending_alerts': self.spending_threshold.value(),
                'savings_alerts': self.savings_threshold.value(),
                'debt_alerts': self.debt_threshold.value()
            }
            
            insight_preferences = {
                key: checkbox.isChecked()
                for key, checkbox in self.insight_checkboxes.items()
            }
            
            if self.parent.app.update_user_preferences(
                alert_thresholds=alert_thresholds,
                insight_preferences=insight_preferences,
                notification_frequency=self.frequency_select.currentText(),
                risk_tolerance=self.risk_select.currentText()
            ):
                self.parent.show_success('Settings updated successfully')
                self.parent.show_dashboard()
                self.accept()
            else:
                self.parent.show_error('Failed to update settings')
                
        except Exception as e:
            self.parent.show_error(f'Error saving settings: {str(e)}')
