"""Debt management service for the Financial Planner application."""
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.models import Debt, Transaction, TransactionType

class DebtService:
    """Service for managing debts and payment strategies."""

    def create_debt(
        self,
        db: Session,
        user_id: int,
        name: str,
        total_amount: float,
        interest_rate: float,
        minimum_payment: float,
        due_date: Optional[datetime] = None
    ) -> Debt:
        """Create a new debt record."""
        debt = Debt(
            user_id=user_id,
            name=name,
            total_amount=total_amount,
            remaining_amount=total_amount,
            interest_rate=interest_rate,
            minimum_payment=minimum_payment,
            due_date=due_date
        )
        db.add(debt)
        db.commit()
        db.refresh(debt)
        return debt

    def record_payment(
        self,
        db: Session,
        debt_id: int,
        amount: float,
        date: Optional[datetime] = None
    ) -> Tuple[Debt, Transaction]:
        """Record a payment towards a debt."""
        debt = db.query(Debt).filter(Debt.id == debt_id).first()
        if not debt:
            raise ValueError("Debt not found")

        if amount > debt.remaining_amount:
            amount = debt.remaining_amount

        debt.remaining_amount -= amount
        
        transaction = Transaction(
            user_id=debt.user_id,
            type=TransactionType.DEBT_PAYMENT,
            amount=amount,
            category="debt_payment",
            description=f"Payment towards {debt.name}",
            date=date or datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(debt)
        db.refresh(transaction)
        
        return debt, transaction

    def get_debt_summary(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, any]:
        """Get summary of all debts for a user."""
        debts = db.query(Debt).filter(Debt.user_id == user_id).all()
        
        total_debt = sum(debt.remaining_amount for debt in debts)
        total_original = sum(debt.total_amount for debt in debts)
        total_paid = total_original - total_debt
        
        return {
            "total_debt": total_debt,
            "total_original": total_original,
            "total_paid": total_paid,
            "progress_percentage": (total_paid / total_original * 100) if total_original > 0 else 0,
            "debts": [
                {
                    "id": debt.id,
                    "name": debt.name,
                    "remaining": debt.remaining_amount,
                    "total": debt.total_amount,
                    "interest_rate": debt.interest_rate,
                    "minimum_payment": debt.minimum_payment,
                    "progress_percentage": (
                        (debt.total_amount - debt.remaining_amount) / debt.total_amount * 100
                        if debt.total_amount > 0 else 0
                    )
                }
                for debt in debts
            ]
        }

    def get_payment_strategy(
        self,
        db: Session,
        user_id: int,
        monthly_budget: float,
        strategy: str = "avalanche"
    ) -> List[Dict[str, any]]:
        """Generate debt payment strategy (avalanche or snowball method)."""
        debts = db.query(Debt).filter(
            Debt.user_id == user_id,
            Debt.remaining_amount > 0
        ).all()
        
        # Calculate total minimum payments
        total_minimum = sum(debt.minimum_payment for debt in debts)
        if total_minimum > monthly_budget:
            raise ValueError("Monthly budget is less than total minimum payments required")
        
        extra_money = monthly_budget - total_minimum
        
        # Sort debts according to strategy
        if strategy == "avalanche":
            # Sort by highest interest rate first
            sorted_debts = sorted(debts, key=lambda x: (-x.interest_rate, x.remaining_amount))
        else:  # snowball
            # Sort by lowest remaining amount first
            sorted_debts = sorted(debts, key=lambda x: (x.remaining_amount, -x.interest_rate))
        
        payment_plan = []
        for debt in sorted_debts:
            payment = {
                "debt_id": debt.id,
                "name": debt.name,
                "minimum_payment": debt.minimum_payment,
                "remaining_amount": debt.remaining_amount,
                "interest_rate": debt.interest_rate,
                "suggested_payment": debt.minimum_payment
            }
            
            # Add extra money to the first debt in the strategy
            if extra_money > 0 and debt == sorted_debts[0]:
                payment["suggested_payment"] += extra_money
                
            payment_plan.append(payment)
            
        return payment_plan

    def calculate_payoff_timeline(
        self,
        db: Session,
        user_id: int,
        monthly_budget: float,
        strategy: str = "avalanche"
    ) -> List[Dict[str, any]]:
        """Calculate projected payoff timeline based on payment strategy."""
        payment_strategy = self.get_payment_strategy(db, user_id, monthly_budget, strategy)
        debts = {
            debt.id: {
                "remaining": debt.remaining_amount,
                "rate": debt.interest_rate / 12,  # Monthly interest rate
                "name": debt.name
            }
            for debt in db.query(Debt).filter(Debt.user_id == user_id).all()
        }
        
        timeline = []
        months = 0
        total_paid = 0
        
        while any(debt["remaining"] > 0 for debt in debts.values()) and months < 360:  # 30-year maximum
            month_data = {
                "month": months + 1,
                "payments": [],
                "total_remaining": 0
            }
            
            for payment in payment_strategy:
                debt = debts[payment["debt_id"]]
                if debt["remaining"] > 0:
                    # Calculate interest
                    interest = debt["remaining"] * debt["rate"]
                    debt["remaining"] += interest
                    
                    # Apply payment
                    payment_amount = min(payment["suggested_payment"], debt["remaining"])
                    debt["remaining"] -= payment_amount
                    total_paid += payment_amount
                    
                    month_data["payments"].append({
                        "debt_name": debt["name"],
                        "payment": payment_amount,
                        "interest": interest,
                        "remaining": debt["remaining"]
                    })
            
            month_data["total_remaining"] = sum(debt["remaining"] for debt in debts.values())
            month_data["total_paid"] = total_paid
            timeline.append(month_data)
            months += 1
            
            # Recalculate payment strategy if a debt is paid off
            if any(debt["remaining"] <= 0 for debt in debts.values()):
                payment_strategy = [
                    payment for payment in payment_strategy
                    if debts[payment["debt_id"]]["remaining"] > 0
                ]
        
        return timeline

    def get_payment_history(
        self,
        db: Session,
        debt_id: int
    ) -> List[Dict[str, any]]:
        """Get payment history for a specific debt."""
        debt = db.query(Debt).filter(Debt.id == debt_id).first()
        if not debt:
            raise ValueError("Debt not found")
            
        payments = db.query(Transaction).filter(
            Transaction.user_id == debt.user_id,
            Transaction.type == TransactionType.DEBT_PAYMENT,
            Transaction.description.like(f"%{debt.name}%")
        ).order_by(Transaction.date.desc()).all()
        
        return [
            {
                "date": payment.date,
                "amount": payment.amount,
                "description": payment.description
            }
            for payment in payments
        ]
