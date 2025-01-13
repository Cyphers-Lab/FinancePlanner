"""Database models for the Financial Planner application."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, JSON, Text
from sqlalchemy.orm import relationship
import enum
from .base import Base

class EmploymentType(enum.Enum):
    """Enum for employment types."""
    PAYEE = "payee"  # Pay-As-You-Earn Employee
    SELF_EMPLOYED = "self_employed"
    BUSINESS_OWNER = "business_owner"
    MIXED = "mixed"

class TaxCategory(enum.Enum):
    """Enum for tax categories."""
    DEDUCTIBLE = "deductible"
    NON_DEDUCTIBLE = "non_deductible"
    TAX_CREDIT = "tax_credit"
    EXEMPT = "exempt"

class TransactionType(enum.Enum):
    """Enum for transaction types."""
    INCOME = "income"
    EXPENSE = "expense"
    DEBT_PAYMENT = "debt_payment"
    INVESTMENT = "investment"
    SAVINGS = "savings"

class SavingsGoalPriority(enum.Enum):
    """Enum for savings goal priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SavingsGoalType(enum.Enum):
    """Enum for savings goal types."""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    EMERGENCY_FUND = "emergency_fund"

class User(Base):
    """User model for storing user account information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    currency = Column(String(1), default='$')  # Currency symbol
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    budgets = relationship("Budget", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    savings_goals = relationship("SavingsGoal", back_populates="user")
    debts = relationship("Debt", back_populates="user")
    investments = relationship("Investment", back_populates="user")

class Budget(Base):
    """Budget model for storing budget categories and limits."""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    month = Column(DateTime, nullable=False)
    alert_threshold = Column(Float, default=0.8)  # Alert at 80% by default
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    transactions = relationship("Transaction", back_populates="budget")

class Transaction(Base):
    """Transaction model for storing all financial transactions."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    budget_id = Column(Integer, ForeignKey("budgets.id"))
    savings_goal_id = Column(Integer, ForeignKey("savings_goals.id"))
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    category = Column(String(50), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    recurring = Column(Boolean, default=False)
    
    # Tax-related fields
    tax_category = Column(Enum(TaxCategory))
    tax_deductible_amount = Column(Float)
    tax_notes = Column(String(500))
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    budget = relationship("Budget", back_populates="transactions")
    savings_goal = relationship("SavingsGoal", back_populates="transactions")

class SavingsGoal(Base):
    """SavingsGoal model for tracking savings targets."""
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    start_date = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime)
    priority = Column(Enum(SavingsGoalPriority), nullable=False, default=SavingsGoalPriority.MEDIUM)
    goal_type = Column(Enum(SavingsGoalType), nullable=False, default=SavingsGoalType.ONE_TIME)
    is_paused = Column(Boolean, default=False)
    allocation_rules = Column(JSON)  # Store rules as JSON: {"percentage": 20} or {"fixed_amount": 500}
    recurring_period = Column(String(50))  # monthly, yearly, etc. for recurring goals
    
    # Emergency fund specific fields
    monthly_expenses = Column(Float)  # For emergency fund calculation
    months_coverage = Column(Float)  # Number of months of expenses to cover (e.g., 3-6)
    critical_threshold = Column(Float)  # Percentage threshold for alerts (e.g., 0.5 for 50%)
    last_withdrawal = Column(DateTime)  # Track last emergency fund withdrawal
    
    # Relationships
    user = relationship("User", back_populates="savings_goals")
    transactions = relationship("Transaction", back_populates="savings_goal")
    alerts = relationship("EmergencyFundAlert", back_populates="savings_goal")

class EmergencyFundAlert(Base):
    """Model for tracking emergency fund alerts."""
    __tablename__ = "emergency_fund_alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    savings_goal_id = Column(Integer, ForeignKey("savings_goals.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # threshold_breach, withdrawal_made, goal_achieved
    threshold_value = Column(Float)  # The threshold that triggered the alert
    current_balance = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="emergency_fund_alerts")
    savings_goal = relationship("SavingsGoal", back_populates="alerts")

class Debt(Base):
    """Debt model for tracking various types of debt."""
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    minimum_payment = Column(Float, nullable=False)
    due_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="debts")

class RecurringFrequency(enum.Enum):
    """Enum for recurring transaction frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class AssetType(enum.Enum):
    """Enum for asset types."""
    CASH = "cash"
    BANK_ACCOUNT = "bank_account"
    INVESTMENT = "investment"
    REAL_ESTATE = "real_estate"
    VEHICLE = "vehicle"
    OTHER = "other"

class ForecastType(enum.Enum):
    """Enum for forecast types."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class InsightType(enum.Enum):
    """Enum for insight types."""
    SPENDING_PATTERN = "spending_pattern"
    SAVINGS_OPPORTUNITY = "savings_opportunity"
    INVESTMENT_SUGGESTION = "investment_suggestion"
    BUDGET_ALERT = "budget_alert"
    DEBT_MANAGEMENT = "debt_management"

class InsightPriority(enum.Enum):
    """Enum for insight priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class UserPreferences(Base):
    """User preferences for insights and notifications."""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_thresholds = Column(JSON, default={
        "spending_alerts": 0.8,  # Alert at 80% of budget
        "savings_alerts": 0.2,   # Alert when savings drop below 20% of income
        "debt_alerts": 0.3,      # Alert when debt payments exceed 30% of income
        "emergency_fund": {
            "critical": 0.5,     # Alert when fund drops below 50% of target
            "warning": 0.75,     # Warning when fund drops below 75% of target
            "withdrawal": True    # Alert on any withdrawal from emergency fund
        }
    })
    insight_preferences = Column(JSON, default={
        "spending_patterns": True,
        "savings_opportunities": True,
        "investment_suggestions": True,
        "budget_alerts": True,
        "debt_management": True,
        "emergency_fund": True
    })
    notification_frequency = Column(String(20), default="daily")  # daily, weekly, monthly
    risk_tolerance = Column(String(20), default="moderate")  # conservative, moderate, aggressive
    
    # Relationships
    user = relationship("User", back_populates="preferences")

class Insight(Base):
    """Model for storing financial insights and recommendations."""
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(InsightType), nullable=False)
    priority = Column(Enum(InsightPriority), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    insight_metadata = Column(JSON)  # Store additional data like affected categories, amounts, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # When this insight becomes irrelevant
    is_read = Column(Boolean, default=False)
    is_acted_upon = Column(Boolean, default=False)
    feedback_rating = Column(Integer)  # User rating of insight usefulness (1-5)
    
    # Relationships
    user = relationship("User", back_populates="insights")

class Investment(Base):
    """Investment model for tracking various investments."""
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)  # stock, crypto, mutual_fund, etc.
    symbol = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    currency = Column(String(3), default='USD')  # ISO 4217 currency code
    
    # Relationships
    user = relationship("User", back_populates="investments")

class TaxProfile(Base):
    """Tax profile model for storing user's tax-related information."""
    __tablename__ = "tax_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employment_type = Column(Enum(EmploymentType), nullable=False)
    tax_id = Column(String(50))  # SSN or Tax ID number
    filing_status = Column(String(50))  # single, married_joint, married_separate, etc.
    withholding_rate = Column(Float)  # For PAYEE employees
    estimated_tax_rate = Column(Float)  # For self-employed/business owners
    tax_year = Column(Integer, nullable=False)
    custom_tax_brackets = Column(JSON)  # Store custom tax brackets if needed
    deduction_preferences = Column(JSON)  # Store preferred deduction method (standard vs itemized)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tax_profile")

class TaxReport(Base):
    """Model for storing generated tax reports."""
    __tablename__ = "tax_reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tax_year = Column(Integer, nullable=False)
    generated_date = Column(DateTime, default=datetime.utcnow)
    total_income = Column(Float, nullable=False)
    total_deductions = Column(Float, nullable=False)
    estimated_tax_liability = Column(Float, nullable=False)
    report_data = Column(JSON, nullable=False)  # Detailed report data
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="tax_reports")

# Update User model relationships
User.emergency_fund_alerts = relationship("EmergencyFundAlert", back_populates="user")
User.preferences = relationship("UserPreferences", uselist=False, back_populates="user")
User.insights = relationship("Insight", back_populates="user")
User.tax_profile = relationship("TaxProfile", uselist=False, back_populates="user")
User.tax_reports = relationship("TaxReport", back_populates="user")

class RecurringTransaction(Base):
    """Model for tracking recurring transactions."""
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    frequency = Column(Enum(RecurringFrequency), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)  # Optional end date for temporary recurring transactions
    last_occurrence = Column(DateTime)  # Track last transaction generated
    next_occurrence = Column(DateTime, nullable=False)  # Next expected transaction date
    is_active = Column(Boolean, default=True)
    description = Column(String(200))
    
    # Relationships
    user = relationship("User", back_populates="recurring_transactions")

class CashFlowForecast(Base):
    """Model for storing cash flow forecasts."""
    __tablename__ = "cash_flow_forecasts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    forecast_type = Column(Enum(ForecastType), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    forecast_data = Column(JSON, nullable=False)  # Store daily/weekly/monthly predictions
    created_at = Column(DateTime, default=datetime.utcnow)
    accuracy_score = Column(Float)  # Track forecast accuracy for improvement
    forecast_metadata = Column(JSON)  # Store additional forecast parameters and settings
    
    # Relationships
    user = relationship("User", back_populates="forecasts")

class Asset(Base):
    """Model for tracking various types of assets."""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum(AssetType), nullable=False)
    value = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    description = Column(String(500))
    asset_metadata = Column(JSON)  # Store additional asset-specific data
    is_liquid = Column(Boolean, default=False)
    is_manual = Column(Boolean, default=True)  # Whether value needs manual updates
    institution = Column(String(100))  # Financial institution if applicable
    account_number = Column(String(100))  # For bank accounts/investments
    
    # Relationships
    user = relationship("User", back_populates="assets")

class NetWorthSnapshot(Base):
    """Model for tracking net worth over time."""
    __tablename__ = "net_worth_snapshots"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_assets = Column(Float, nullable=False)
    total_liabilities = Column(Float, nullable=False)
    net_worth = Column(Float, nullable=False)
    snapshot_data = Column(JSON)  # Detailed breakdown of assets and liabilities
    notes = Column(String(500))  # For recording significant events/changes
    
    # Relationships
    user = relationship("User", back_populates="net_worth_snapshots")

class NetWorthGoal(Base):
    """Model for tracking net worth goals."""
    __tablename__ = "net_worth_goals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_amount = Column(Float, nullable=False)
    target_date = Column(DateTime, nullable=False)
    start_amount = Column(Float, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    description = Column(String(500))
    is_achieved = Column(Boolean, default=False)
    achieved_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="net_worth_goals")

# Update User model relationships
User.recurring_transactions = relationship("RecurringTransaction", back_populates="user")
User.forecasts = relationship("CashFlowForecast", back_populates="user")
User.assets = relationship("Asset", back_populates="user")
User.net_worth_snapshots = relationship("NetWorthSnapshot", back_populates="user")
User.net_worth_goals = relationship("NetWorthGoal", back_populates="user")
