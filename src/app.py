"""Main application class for the Financial Planner."""
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from .models.base import get_db, Base, engine
from .models.models import TransactionType, UserPreferences
from .utils.currency import format_currency
from .services.auth_service import AuthService
from .services.budget_service import BudgetService
from .services.transaction_service import TransactionService
from .services.debt_service import DebtService
from .services.investment_service import InvestmentService
from .services.report_service import ReportService
from .services.savings_service import SavingsService
from .services.insights_service import InsightsService
from .services.tax_service import TaxService
from .services.forecast_service import ForecastService

class FinancialPlanner:
    """Main application class that coordinates all financial planning functionality."""

    def __init__(self):
        """Initialize the Financial Planner application."""
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        # Initialize services
        self.auth_service = AuthService()
        self.budget_service = BudgetService()
        self.transaction_service = TransactionService()
        self.debt_service = DebtService()
        self.investment_service = InvestmentService()
        self.report_service = ReportService()
        self.savings_service = SavingsService()
        self.insights_service = InsightsService(None)  # Will be initialized with session
        self.tax_service = TaxService(None)  # Will be initialized with session
        self.forecast_service = ForecastService(None)  # Will be initialized with session
        
        # Current session state
        self.current_user = None
        self.db: Optional[Session] = None

    def initialize_session(self):
        """Initialize a new database session."""
        self.db = next(get_db())
        self.insights_service.db = self.db
        self.tax_service = TaxService(self.db)
        self.forecast_service = ForecastService(self.db)

    def close_session(self):
        """Close the current database session."""
        if self.db:
            self.db.close()
            self.db = None

    def login(self, username: str, password: str) -> bool:
        """Log in a user."""
        try:
            self.initialize_session()
            user = self.auth_service.authenticate_user(self.db, username, password)
            if user:
                self.current_user = user
                return True
            return False
        except Exception as e:
            print(f"Login error: {e}")
            return False

    def register(self, username: str, email: str, password: str, currency: str = '$') -> bool:
        """Register a new user."""
        try:
            self.initialize_session()
            user = self.auth_service.create_user(self.db, username, email, password, currency)
            self.current_user = user
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False

    def update_currency(self, currency: str) -> bool:
        """Update the user's preferred currency."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        try:
            self.current_user = self.auth_service.update_user_currency(
                self.db,
                self.current_user.id,
                currency
            )
            return True
        except Exception as e:
            print(f"Currency update error: {e}")
            return False

    def format_amount(self, amount: float) -> str:
        """Format an amount using the user's preferred currency."""
        if not self.current_user:
            return format_currency(amount)
        return format_currency(amount, self.current_user.currency)

    def logout(self):
        """Log out the current user."""
        self.current_user = None
        self.close_session()

    def create_budget(self, category: str, amount: float, month: datetime) -> Dict[str, Any]:
        """Create a new budget category."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        budget = self.budget_service.create_budget(
            self.db,
            self.current_user.id,
            category,
            amount,
            month
        )
        return {
            "id": budget.id,
            "category": budget.category,
            "amount": budget.amount,
            "month": budget.month
        }

    def add_transaction(
        self,
        amount: float,
        category: str,
        transaction_type: str,
        description: Optional[str] = None,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Add a new transaction."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        # Convert string type to enum
        try:
            transaction_type_enum = TransactionType(transaction_type.lower())
        except ValueError:
            raise ValueError(f"Invalid transaction type: {transaction_type}")
            
        transaction = self.transaction_service.create_transaction(
            self.db,
            self.current_user.id,
            amount,
            category,
            transaction_type_enum,
            description,
            date=date
        )
        return {
            "id": transaction.id,
            "amount": transaction.amount,
            "category": transaction.category,
            "type": transaction.type.value,
            "date": transaction.date
        }

    def get_budget_summary(self, month: Optional[datetime] = None) -> Dict[str, Any]:
        """Get budget summary for the current user."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.budget_service.get_budget_summary(
            self.db,
            self.current_user.id,
            month
        )

    def get_financial_health(self) -> Dict[str, Any]:
        """Get financial health score and insights."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.report_service.calculate_financial_health_score(
            self.db,
            self.current_user.id
        )

    def generate_monthly_report(self, month: datetime, output_format: str = "pdf") -> str:
        """Generate a monthly financial report."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        report_data = self.report_service.generate_monthly_report(
            self.db,
            self.current_user.id,
            month
        )
        
        if output_format == "pdf":
            output_path = os.path.join(
                "reports",
                f"financial_report_{month.strftime('%Y_%m')}.pdf"
            )
            os.makedirs("reports", exist_ok=True)
            return self.report_service.export_to_pdf(report_data, output_path)
            
        return report_data

    def add_investment(
        self,
        investment_type: str,
        symbol: str,
        quantity: float,
        purchase_price: float,
        currency: str = 'USD'
    ) -> Dict[str, Any]:
        """Add a new investment."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        investment = self.investment_service.create_investment(
            self.db,
            self.current_user.id,
            investment_type,
            symbol,
            quantity,
            purchase_price,
            currency
        )
        return {
            "id": investment.id,
            "type": investment.type,
            "symbol": investment.symbol,
            "quantity": investment.quantity,
            "purchase_price": investment.purchase_price
        }

    def add_debt(
        self,
        name: str,
        total_amount: float,
        interest_rate: float,
        minimum_payment: float,
        due_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Add a new debt."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        debt = self.debt_service.create_debt(
            self.db,
            self.current_user.id,
            name,
            total_amount,
            interest_rate,
            minimum_payment,
            due_date
        )
        return {
            "id": debt.id,
            "name": debt.name,
            "total_amount": debt.total_amount,
            "remaining_amount": debt.remaining_amount,
            "interest_rate": debt.interest_rate
        }

    def get_debt_payment_strategy(
        self,
        monthly_budget: float,
        strategy: str = "avalanche"
    ) -> Dict[str, Any]:
        """Get debt payment strategy."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.debt_service.get_payment_strategy(
            self.db,
            self.current_user.id,
            monthly_budget,
            strategy
        )

    def update_investment_price(self, investment_id: int, current_price: float) -> Dict[str, Any]:
        """Update the current price of an investment."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        investment = self.investment_service.update_investment_price(
            self.db,
            investment_id,
            current_price
        )
        return {
            "id": investment.id,
            "type": investment.type,
            "symbol": investment.symbol,
            "quantity": investment.quantity,
            "purchase_price": investment.purchase_price
        }

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get investment portfolio summary."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.investment_service.get_portfolio_value(
            self.db,
            self.current_user.id
        )

    def get_debt_summary(self) -> Dict[str, Any]:
        """Get debt summary for the current user."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.debt_service.get_debt_summary(
            self.db,
            self.current_user.id
        )

    def create_savings_goal(
        self,
        name: str,
        target_amount: float,
        description: Optional[str] = None,
        target_date: Optional[datetime] = None,
        priority: str = "medium",
        goal_type: str = "one_time",
        allocation_rules: Optional[Dict[str, Any]] = None,
        recurring_period: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new savings goal."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        from .models.models import SavingsGoalPriority, SavingsGoalType
        
        goal = self.savings_service.create_goal(
            self.db,
            self.current_user.id,
            name,
            target_amount,
            description,
            target_date,
            SavingsGoalPriority[priority.upper()],
            SavingsGoalType[goal_type.upper()],
            allocation_rules,
            recurring_period
        )
        
        return {
            "id": goal.id,
            "name": goal.name,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "progress": (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        }

    def get_savings_goals(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        """Get all savings goals for the current user."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        goals = self.savings_service.get_user_goals(
            self.db,
            self.current_user.id,
            include_completed
        )
        
        return [{
            "id": goal.id,
            "name": goal.name,
            "description": goal.description,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "progress": (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0,
            "target_date": goal.target_date,
            "priority": goal.priority.value,
            "goal_type": goal.goal_type.value,
            "is_paused": goal.is_paused,
            "allocation_rules": goal.allocation_rules,
            # Emergency fund specific fields
            "monthly_expenses": goal.monthly_expenses,
            "months_coverage": goal.months_coverage,
            "critical_threshold": goal.critical_threshold,
            "last_withdrawal": goal.last_withdrawal
        } for goal in goals]

    def update_savings_goal(
        self,
        goal_id: int,
        target_amount: Optional[float] = None,
        target_date: Optional[datetime] = None,
        priority: Optional[str] = None,
        allocation_rules: Optional[Dict[str, Any]] = None,
        is_paused: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update an existing savings goal."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        from .models.models import SavingsGoalPriority
        
        goal = self.savings_service.update_goal(
            self.db,
            goal_id,
            target_amount,
            target_date,
            SavingsGoalPriority[priority.upper()] if priority else None,
            allocation_rules,
            is_paused
        )
        
        return {
            "id": goal.id,
            "name": goal.name,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "progress": (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        }

    def delete_savings_goal(self, goal_id: int) -> bool:
        """Delete a savings goal."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.savings_service.delete_goal(self.db, goal_id)

    def get_savings_goal_progress(self, goal_id: int) -> Dict[str, Any]:
        """Get detailed progress information for a goal."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        progress = self.savings_service.get_goal_progress(self.db, goal_id)
        goal = progress["goal"]
        
        return {
            "id": goal.id,
            "name": goal.name,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "progress_percentage": progress["progress_percentage"],
            "monthly_average": progress["monthly_average"],
            "remaining_amount": progress["remaining_amount"],
            "is_completed": progress["is_completed"],
            "recent_transactions": [{
                "date": t.date,
                "amount": t.amount,
                "description": t.description
            } for t in progress["recent_transactions"]]
        }

    def check_savings_alerts(self) -> List[Dict[str, Any]]:
        """Check all savings goals for alerts."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.savings_service.check_goal_alerts(self.db, self.current_user.id)

    def create_emergency_fund(
        self,
        monthly_expenses: float,
        months_coverage: float = 6.0,
        critical_threshold: float = 0.5,
        allocation_rules: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an emergency fund goal."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        goal = self.savings_service.create_emergency_fund(
            self.db,
            self.current_user.id,
            monthly_expenses,
            months_coverage,
            critical_threshold,
            allocation_rules,
            description
        )
        
        return {
            "id": goal.id,
            "name": goal.name,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "progress": (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0,
            "monthly_expenses": goal.monthly_expenses,
            "months_coverage": goal.months_coverage,
            "critical_threshold": goal.critical_threshold
        }

    def record_emergency_withdrawal(
        self,
        goal_id: int,
        amount: float,
        description: str
    ) -> Dict[str, Any]:
        """Record a withdrawal from an emergency fund."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        result = self.savings_service.record_emergency_withdrawal(
            self.db,
            goal_id,
            amount,
            description
        )
        
        return {
            "transaction_id": result["transaction"].id,
            "new_balance": result["new_balance"],
            "months_coverage_remaining": result["months_coverage_remaining"]
        }

    def get_insights(self, insight_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get insights for the current user."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        from .models.models import InsightType
        insight_type_enum = InsightType(insight_type.lower()) if insight_type else None
        
        return self.insights_service.get_user_insights(
            self.current_user.id,
            insight_type=insight_type_enum,
            limit=limit
        )

    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate new insights based on user's financial data."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.insights_service.generate_insights(self.current_user.id)

    def mark_insight_read(self, insight_id: int) -> None:
        """Mark an insight as read."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        self.insights_service.mark_insight_read(insight_id, self.current_user.id)

    def mark_insight_acted_upon(self, insight_id: int) -> None:
        """Mark an insight as acted upon."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        self.insights_service.mark_insight_acted_upon(insight_id, self.current_user.id)

    def rate_insight(self, insight_id: int, rating: int) -> None:
        """Rate an insight's usefulness."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        self.insights_service.rate_insight(insight_id, self.current_user.id, rating)

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences including insight settings."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        preferences = (self.db.query(UserPreferences)
                      .filter_by(user_id=self.current_user.id)
                      .first())
        
        if not preferences:
            # Create default preferences if none exist
            preferences = UserPreferences(user_id=self.current_user.id)
            self.db.add(preferences)
            self.db.commit()
        
        return {
            'alert_thresholds': preferences.alert_thresholds,
            'insight_preferences': preferences.insight_preferences,
            'notification_frequency': preferences.notification_frequency,
            'risk_tolerance': preferences.risk_tolerance
        }

    def get_service(self, service_name: str) -> Any:
        """Get a service by name."""
        services = {
            'auth_service': self.auth_service,
            'budget_service': self.budget_service,
            'transaction_service': self.transaction_service,
            'debt_service': self.debt_service,
            'investment_service': self.investment_service,
            'report_service': self.report_service,
            'savings_service': self.savings_service,
            'insights_service': self.insights_service,
            'tax_service': self.tax_service,
            'forecast_service': self.forecast_service
        }
        return services.get(service_name)

    def update_user_preferences(
        self,
        alert_thresholds: Optional[Dict[str, float]] = None,
        insight_preferences: Optional[Dict[str, bool]] = None,
        notification_frequency: Optional[str] = None,
        risk_tolerance: Optional[str] = None
    ) -> bool:
        """Update user preferences."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        try:
            preferences = (self.db.query(UserPreferences)
                         .filter_by(user_id=self.current_user.id)
                         .first())
            
            if alert_thresholds is not None:
                preferences.alert_thresholds = alert_thresholds
            if insight_preferences is not None:
                preferences.insight_preferences = insight_preferences
            if notification_frequency is not None:
                preferences.notification_frequency = notification_frequency
            if risk_tolerance is not None:
                preferences.risk_tolerance = risk_tolerance
                
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return False

    def detect_recurring_transactions(self, lookback_months: int = 6) -> List[Dict[str, Any]]:
        """Detect recurring transaction patterns."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        return self.forecast_service.detect_recurring_transactions(
            self.current_user.id,
            lookback_months
        )

    def create_recurring_transaction(
        self,
        name: str,
        tx_type: str,
        amount: float,
        category: str,
        frequency: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create a new recurring transaction."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        from .models.models import TransactionType, RecurringFrequency
        
        recurring_tx = self.forecast_service.create_recurring_transaction(
            user_id=self.current_user.id,
            name=name,
            tx_type=TransactionType(tx_type.lower()),
            amount=amount,
            category=category,
            frequency=RecurringFrequency(frequency.lower()),
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "id": recurring_tx.id,
            "name": recurring_tx.name,
            "type": recurring_tx.type.value,
            "amount": recurring_tx.amount,
            "category": recurring_tx.category,
            "frequency": recurring_tx.frequency.value,
            "next_occurrence": recurring_tx.next_occurrence
        }

    def generate_forecast(
        self,
        forecast_type: str,
        periods: int = 12,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate a cash flow forecast."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        from .models.models import ForecastType
        
        forecast = self.forecast_service.generate_forecast(
            user_id=self.current_user.id,
            forecast_type=ForecastType(forecast_type.lower()),
            start_date=start_date,
            periods=periods
        )
        
        return {
            "id": forecast.id,
            "type": forecast.forecast_type.value,
            "start_date": forecast.start_date,
            "end_date": forecast.end_date,
            "forecast_data": forecast.forecast_data,
            "metadata": forecast.forecast_metadata
        }

    def get_latest_forecast(self, forecast_type: str) -> Optional[Dict[str, Any]]:
        """Get the most recent forecast of the specified type."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        from .models.models import ForecastType
        
        forecast = self.forecast_service.get_latest_forecast(
            user_id=self.current_user.id,
            forecast_type=ForecastType(forecast_type.lower())
        )
        
        if forecast:
            return {
                "id": forecast.id,
                "type": forecast.forecast_type.value,
                "start_date": forecast.start_date,
                "end_date": forecast.end_date,
                "forecast_data": forecast.forecast_data,
                "metadata": forecast.forecast_metadata
            }
        return None

    def get_transactions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None
    ) -> List[Any]:
        """Get transactions for the current user with optional filters."""
        if not self.current_user:
            raise ValueError("User not logged in")
            
        transactions = self.transaction_service.get_transactions(
            self.db,
            self.current_user.id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            transaction_type=transaction_type
        )
        
        # Convert transactions for frontend
        return [{
            'id': t.id,
            'amount': t.amount,
            'category': t.category,
            'type': t.type.value,  # Convert enum to string
            'date': t.date,
            'description': t.description
        } for t in transactions]
