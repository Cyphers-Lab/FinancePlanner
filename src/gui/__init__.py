"""GUI package for the Financial Planner application."""
from .main_window import MainWindow
from .pages.login_page import LoginPage
from .pages.dashboard_page import DashboardPage
from .pages.budget_page import BudgetPage
from .pages.transaction_page import TransactionPage
from .pages.investment_page import InvestmentPage
from .pages.debt_page import DebtPage
from .pages.report_page import ReportPage

__all__ = [
    'MainWindow',
    'LoginPage',
    'DashboardPage',
    'BudgetPage',
    'TransactionPage',
    'InvestmentPage',
    'DebtPage',
    'ReportPage'
]
