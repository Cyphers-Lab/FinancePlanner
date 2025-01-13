"""Budget management service for the Financial Planner application."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.models import Budget, Transaction, TransactionType

class BudgetService:
    """Service for managing budgets and tracking expenses."""

    def create_budget(
        self, 
        db: Session, 
        user_id: int, 
        category: str, 
        amount: float,
        month: datetime,
        alert_threshold: float = 0.8
    ) -> Budget:
        """Create a new budget category for a user."""
        budget = Budget(
            user_id=user_id,
            category=category,
            amount=amount,
            month=month,
            alert_threshold=alert_threshold
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget

    def get_user_budgets(
        self, 
        db: Session, 
        user_id: int, 
        month: Optional[datetime] = None
    ) -> List[Budget]:
        """Get all budgets for a user, optionally filtered by month."""
        query = db.query(Budget).filter(Budget.user_id == user_id)
        if month:
            # Extract year and month for comparison using SQLite's strftime
            query = query.filter(
                func.strftime('%Y-%m', Budget.month) == 
                func.strftime('%Y-%m', month)
            )
        return query.all()

    def get_budget_usage(
        self, 
        db: Session, 
        budget_id: int
    ) -> Dict[str, float]:
        """Calculate current usage and remaining amount for a budget."""
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise ValueError("Budget not found")

        # Get total expenses for this budget's category and month
        total_expenses = db.query(func.sum(Transaction.amount))\
            .filter(
                Transaction.user_id == budget.user_id,
                Transaction.category == budget.category,
                func.strftime('%Y-%m', Transaction.date) == func.strftime('%Y-%m', budget.month),
                Transaction.type == TransactionType.EXPENSE
            ).scalar() or 0.0

        remaining = budget.amount - total_expenses
        usage_percentage = (total_expenses / budget.amount) * 100 if budget.amount > 0 else 0

        return {
            "total_budget": budget.amount,
            "spent": total_expenses,
            "remaining": remaining,
            "usage_percentage": usage_percentage
        }

    def check_budget_alerts(
        self, 
        db: Session, 
        user_id: int
    ) -> List[Dict[str, any]]:
        """Check all budgets for a user and return alerts for those exceeding threshold."""
        alerts = []
        budgets = self.get_user_budgets(db, user_id)
        
        for budget in budgets:
            usage = self.get_budget_usage(db, budget.id)
            if usage["usage_percentage"] >= (budget.alert_threshold * 100):
                alerts.append({
                    "budget_id": budget.id,
                    "category": budget.category,
                    "threshold": budget.alert_threshold * 100,
                    "current_usage": usage["usage_percentage"],
                    "remaining": usage["remaining"]
                })
        
        return alerts

    def update_budget(
        self,
        db: Session,
        budget_id: int,
        amount: Optional[float] = None,
        alert_threshold: Optional[float] = None
    ) -> Budget:
        """Update an existing budget's amount or alert threshold."""
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise ValueError("Budget not found")

        if amount is not None:
            budget.amount = amount
        if alert_threshold is not None:
            budget.alert_threshold = alert_threshold

        db.commit()
        db.refresh(budget)
        return budget

    def delete_budget(self, db: Session, budget_id: int) -> bool:
        """Delete a budget category."""
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return False

        db.delete(budget)
        db.commit()
        return True

    def get_budget_summary(
        self,
        db: Session,
        user_id: int,
        month: Optional[datetime] = None
    ) -> Dict[str, any]:
        """Get a summary of all budgets and their usage for a user."""
        budgets = self.get_user_budgets(db, user_id, month)
        summary = {
            "total_budgeted": 0.0,
            "total_spent": 0.0,
            "categories": []
        }

        for budget in budgets:
            usage = self.get_budget_usage(db, budget.id)
            summary["total_budgeted"] += budget.amount
            summary["total_spent"] += usage["spent"]
            summary["categories"].append({
                "category": budget.category,
                "budgeted": budget.amount,
                "spent": usage["spent"],
                "remaining": usage["remaining"],
                "usage_percentage": usage["usage_percentage"]
            })

        summary["total_remaining"] = summary["total_budgeted"] - summary["total_spent"]
        summary["overall_usage_percentage"] = (
            (summary["total_spent"] / summary["total_budgeted"]) * 100
            if summary["total_budgeted"] > 0 else 0
        )

        return summary
