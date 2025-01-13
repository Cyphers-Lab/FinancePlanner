"""Script to generate test data for the Financial Planner."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datetime import datetime, timedelta
from src.models.base import get_db, Base, engine
from src.models.models import (
    User, Transaction, Budget, SavingsGoal, Debt, Investment,
    TransactionType, UserPreferences
)
from src.services.auth_service import AuthService

def create_test_data():
    """Create test data to demonstrate insights feature."""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    auth_service = AuthService()
    
    # Create test user
    test_user = auth_service.create_user(
        db,
        username="test_user",
        email="test@example.com",
        password="password123",
        currency="$"
    )
    
    # Create user preferences
    preferences = UserPreferences(
        user_id=test_user.id,
        alert_thresholds={
            "spending_alerts": 0.8,
            "savings_alerts": 0.2,
            "debt_alerts": 0.3
        },
        insight_preferences={
            "spending_patterns": True,
            "savings_opportunities": True,
            "investment_suggestions": True,
            "budget_alerts": True,
            "debt_management": True
        },
        notification_frequency="daily",
        risk_tolerance="moderate"
    )
    db.add(preferences)
    
    # Create monthly budgets
    budgets = {
        "Groceries": 800,
        "Entertainment": 200,
        "Dining": 400,
        "Transportation": 300,
        "Shopping": 500
    }
    
    for category, amount in budgets.items():
        budget = Budget(
            user_id=test_user.id,
            category=category,
            amount=amount,
            month=datetime.now().replace(day=1)
        )
        db.add(budget)
    
    # Create transactions to demonstrate spending patterns
    # Normal grocery spending
    for i in range(10):
        transaction = Transaction(
            user_id=test_user.id,
            type=TransactionType.EXPENSE,
            amount=75.0,
            category="Groceries",
            description=f"Grocery shopping #{i+1}",
            date=datetime.now() - timedelta(days=i*3)
        )
        db.add(transaction)
    
    # Unusual spike in entertainment spending
    transaction = Transaction(
        user_id=test_user.id,
        type=TransactionType.EXPENSE,
        amount=300.0,  # Significantly higher than budget
        category="Entertainment",
        description="Concert tickets",
        date=datetime.now() - timedelta(days=2)
    )
    db.add(transaction)
    
    # Add monthly income
    transaction = Transaction(
        user_id=test_user.id,
        type=TransactionType.INCOME,
        amount=500000.0,
        category="Salary",
        description="Monthly salary",
        date=datetime.now() - timedelta(days=15)
    )
    db.add(transaction)
    
    # Add high-interest debt
    debt = Debt(
        user_id=test_user.id,
        name="Credit Card Debt",
        total_amount=10000.0,
        remaining_amount=8000.0,
        interest_rate=18.99,
        minimum_payment=200.0,
        due_date=datetime.now() + timedelta(days=15)
    )
    db.add(debt)
    
    # Add some investments
    investments = [
        {
            "type": "stock",
            "symbol": "AAPL",
            "quantity": 10,
            "purchase_price": 150.0
        },
        {
            "type": "stock",
            "symbol": "GOOGL",
            "quantity": 5,
            "purchase_price": 2800.0
        }
    ]
    
    for inv in investments:
        investment = Investment(
            user_id=test_user.id,
            type=inv["type"],
            symbol=inv["symbol"],
            quantity=inv["quantity"],
            purchase_price=inv["purchase_price"]
        )
        db.add(investment)
    
    # Add a savings goal
    goal = SavingsGoal(
        user_id=test_user.id,
        name="Emergency Fund",
        description="6 months of living expenses",
        target_amount=30000.0,
        current_amount=5000.0,
        target_date=datetime.now() + timedelta(days=365)
    )
    db.add(goal)
    
    # Commit all changes
    db.commit()
    db.close()

if __name__ == "__main__":
    create_test_data()
    print("Test data generated successfully!")
