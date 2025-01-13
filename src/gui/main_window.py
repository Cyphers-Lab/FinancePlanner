"""Main window for the Financial Planner GUI application."""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
                           QMessageBox)
from PyQt5.QtCore import Qt
from src.gui.pages.login_page import LoginPage
from src.gui.pages.forecast_page import ForecastPage
from src.gui.pages.dashboard_page import DashboardPage
from src.gui.pages.budget_page import BudgetPage
from src.gui.pages.transaction_page import TransactionPage
from src.gui.pages.investment_page import InvestmentPage
from src.gui.pages.debt_page import DebtPage
from src.gui.pages.report_page import ReportPage
from src.gui.pages.savings_page import SavingsPage
from src.gui.pages.tax_page import TaxPage
from src.gui.pages.net_worth_page import NetWorthPage
from src.app import FinancialPlanner

class MainWindow(QMainWindow):
    """Main window class for the Financial Planner application."""
    
    def __init__(self):
        super().__init__()
        self.app = FinancialPlanner()
        self.app.initialize_session()  # Initialize database session
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Financial Planner')
        self.setMinimumSize(1024, 768)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Initialize pages
        self.login_page = LoginPage(self)
        self.dashboard_page = DashboardPage(self)
        self.budget_page = BudgetPage(self)
        self.transaction_page = TransactionPage(self)
        self.investment_page = InvestmentPage(self)
        self.debt_page = DebtPage(self)
        self.report_page = ReportPage(self)
        self.savings_page = SavingsPage(self)
        self.tax_page = TaxPage(self)
        self.forecast_page = ForecastPage(self)
        self.net_worth_page = NetWorthPage(self)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.budget_page)
        self.stacked_widget.addWidget(self.transaction_page)
        self.stacked_widget.addWidget(self.investment_page)
        self.stacked_widget.addWidget(self.debt_page)
        self.stacked_widget.addWidget(self.report_page)
        self.stacked_widget.addWidget(self.savings_page)
        self.stacked_widget.addWidget(self.tax_page)
        self.stacked_widget.addWidget(self.forecast_page)
        self.stacked_widget.addWidget(self.net_worth_page)
        
        # Start with login page
        self.show_login_page()
        
    def show_login_page(self):
        """Switch to login page."""
        self.stacked_widget.setCurrentWidget(self.login_page)
        
    def show_dashboard(self):
        """Switch to dashboard page."""
        self.stacked_widget.setCurrentWidget(self.dashboard_page)
        self.dashboard_page.refresh_data()
        
    def show_budget_page(self):
        """Switch to budget page."""
        self.stacked_widget.setCurrentWidget(self.budget_page)
        self.budget_page.refresh_data()
        
    def show_transaction_page(self):
        """Switch to transaction page."""
        self.stacked_widget.setCurrentWidget(self.transaction_page)
        self.transaction_page.refresh_data()
        
    def show_investment_page(self):
        """Switch to investment page."""
        self.stacked_widget.setCurrentWidget(self.investment_page)
        self.investment_page.refresh_data()
        
    def show_debt_page(self):
        """Switch to debt page."""
        self.stacked_widget.setCurrentWidget(self.debt_page)
        self.debt_page.refresh_data()
        
    def show_report_page(self):
        """Switch to report page."""
        self.stacked_widget.setCurrentWidget(self.report_page)
        
    def show_savings_page(self):
        """Switch to savings page."""
        self.stacked_widget.setCurrentWidget(self.savings_page)
        self.savings_page.refresh_goals()
        
    def show_tax_page(self):
        """Switch to tax page."""
        self.stacked_widget.setCurrentWidget(self.tax_page)
        self.tax_page.refresh_data()
        
    def show_forecast_page(self):
        """Switch to forecast page."""
        self.stacked_widget.setCurrentWidget(self.forecast_page)
        self.forecast_page.refresh_data()
        
    def show_net_worth_page(self):
        """Switch to net worth page."""
        self.stacked_widget.setCurrentWidget(self.net_worth_page)
        self.net_worth_page.refresh_data()
        
    def handle_login_success(self):
        """Handle successful login."""
        self.show_dashboard()
        
    def handle_logout(self):
        """Handle user logout."""
        self.app.logout()
        self.show_login_page()
        
    def show_error(self, message):
        """Show error message box."""
        QMessageBox.critical(self, 'Error', message)
        
    def show_success(self, message):
        """Show success message box."""
        QMessageBox.information(self, 'Success', message)
