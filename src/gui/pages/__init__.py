"""Pages package for the Financial Planner GUI."""
from .login_page import LoginPage
from .dashboard_page import DashboardPage
from .budget_page import BudgetPage
from .transaction_page import TransactionPage
from .investment_page import InvestmentPage
from .debt_page import DebtPage
from .report_page import ReportPage

__all__ = [
    'LoginPage',
    'DashboardPage',
    'BudgetPage',
    'TransactionPage',
    'InvestmentPage',
    'DebtPage',
    'ReportPage'
]
