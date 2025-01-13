"""Transaction management service for the Financial Planner application."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.models import Transaction, TransactionType, Budget

class TransactionService:
    """Service for managing financial transactions."""

    def create_transaction(
        self,
        db: Session,
        user_id: int,
        amount: float,
        category: str,
        transaction_type: TransactionType,
        description: Optional[str] = None,
        budget_id: Optional[int] = None,
        date: Optional[datetime] = None,
        recurring: bool = False
    ) -> Transaction:
        """Create a new transaction."""
        # Use provided date or current time
        transaction_date = date or datetime.utcnow()
        
        # If no budget_id provided and it's an expense, try to find matching budget
        if budget_id is None and transaction_type == TransactionType.EXPENSE:
            # Find budget for this category and month
            budget = db.query(Budget).filter(
                Budget.user_id == user_id,
                Budget.category == category,
                func.strftime('%Y-%m', Budget.month) == func.strftime('%Y-%m', transaction_date)
            ).first()
            
            if budget:
                budget_id = budget.id
        
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            category=category,
            type=transaction_type,
            description=description,
            budget_id=budget_id,
            date=transaction_date,
            recurring=recurring
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    def get_transactions(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Transaction]:
        """Get transactions with optional filters."""
        query = db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if category:
            query = query.filter(Transaction.category == category)
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
            
        return query.order_by(Transaction.date.desc()).all()

    def get_recurring_transactions(
        self,
        db: Session,
        user_id: int
    ) -> List[Transaction]:
        """Get all recurring transactions for a user."""
        return db.query(Transaction)\
            .filter(
                Transaction.user_id == user_id,
                Transaction.recurring == True
            ).all()

    def update_transaction(
        self,
        db: Session,
        transaction_id: int,
        amount: Optional[float] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        date: Optional[datetime] = None,
        recurring: Optional[bool] = None
    ) -> Transaction:
        """Update an existing transaction."""
        transaction = db.query(Transaction)\
            .filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        if amount is not None:
            transaction.amount = amount
        if category is not None:
            transaction.category = category
        if description is not None:
            transaction.description = description
        if date is not None:
            transaction.date = date
        if recurring is not None:
            transaction.recurring = recurring

        db.commit()
        db.refresh(transaction)
        return transaction

    def delete_transaction(
        self,
        db: Session,
        transaction_id: int
    ) -> bool:
        """Delete a transaction."""
        transaction = db.query(Transaction)\
            .filter(Transaction.id == transaction_id).first()
        if not transaction:
            return False

        db.delete(transaction)
        db.commit()
        return True

    def get_category_summary(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Dict[str, any]]:
        """Get summary of transactions by category."""
        query = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(Transaction.user_id == user_id)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)

        return [
            {
                "category": category,
                "total_amount": float(total_amount),
                "transaction_count": transaction_count
            }
            for category, total_amount, transaction_count
            in query.group_by(Transaction.category).all()
        ]

    def auto_categorize_transaction(
        self,
        db: Session,
        user_id: int,
        description: str,
        amount: float
    ) -> Optional[str]:
        """Attempt to automatically categorize a transaction based on history."""
        # Find the most common category for similar transactions
        similar_transaction = db.query(Transaction)\
            .filter(
                Transaction.user_id == user_id,
                Transaction.description.ilike(f"%{description}%")
            ).order_by(Transaction.date.desc()).first()

        if similar_transaction:
            return similar_transaction.category

        # If no similar description, try to match based on amount for recurring transactions
        amount_match = db.query(Transaction)\
            .filter(
                Transaction.user_id == user_id,
                Transaction.amount == amount,
                Transaction.recurring == True
            ).order_by(Transaction.date.desc()).first()

        if amount_match:
            return amount_match.category

        return None

    def get_monthly_totals(
        self,
        db: Session,
        user_id: int,
        year: int,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Dict[str, any]]:
        """Get monthly totals for a specific year."""
        query = db.query(
            func.date_trunc('month', Transaction.date).label('month'),
            func.sum(Transaction.amount).label('total_amount')
        ).filter(
            Transaction.user_id == user_id,
            func.extract('year', Transaction.date) == year
        )

        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)

        return [
            {
                "month": month,
                "total_amount": float(total_amount)
            }
            for month, total_amount
            in query.group_by(text('month')).order_by(text('month')).all()
        ]
