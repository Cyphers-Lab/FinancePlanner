"""Investment management service for the Financial Planner application."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import requests
import os
from ..models.models import Investment, Transaction, TransactionType

class InvestmentService:
    """Service for managing investments and tracking market data."""

    def __init__(self):
        """Initialize the investment service."""
        pass

    def update_investment_price(
        self,
        db: Session,
        investment_id: int,
        current_price: float
    ) -> Investment:
        """Update the current price of an investment."""
        investment = db.query(Investment).filter(Investment.id == investment_id).first()
        if not investment:
            raise ValueError("Investment not found")
            
        # Create a price update transaction
        transaction = Transaction(
            user_id=investment.user_id,
            type=TransactionType.INVESTMENT,
            amount=current_price * investment.quantity,
            category=f"{investment.type}_price_update",
            description=f"Price update for {investment.symbol}: ${current_price}",
            date=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        return investment

    def create_investment(
        self,
        db: Session,
        user_id: int,
        investment_type: str,
        symbol: str,
        quantity: float,
        purchase_price: float,
        currency: str = 'USD',
        purchase_date: Optional[datetime] = None
    ) -> Investment:
        """Create a new investment record."""
        investment = Investment(
            user_id=user_id,
            type=investment_type,
            symbol=symbol,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_date=purchase_date or datetime.utcnow(),
            currency=currency.upper()
        )
        
        # Record the investment as a transaction
        transaction = Transaction(
            user_id=user_id,
            type=TransactionType.INVESTMENT,
            amount=quantity * purchase_price,
            category=f"{investment_type}_investment",
            description=f"Investment in {symbol}",
            date=investment.purchase_date
        )
        
        db.add(investment)
        db.add(transaction)
        db.commit()
        db.refresh(investment)
        return investment

    def get_latest_price(
        self,
        db: Session,
        investment_id: int
    ) -> Optional[float]:
        """Get the latest price for an investment from transaction history."""
        latest_price_update = db.query(Transaction).filter(
            Transaction.type == TransactionType.INVESTMENT,
            Transaction.description.like(f"Price update for%")
        ).order_by(Transaction.date.desc()).first()
        
        if latest_price_update:
            # Extract price from description (format: "Price update for SYMBOL: $PRICE")
            try:
                price_str = latest_price_update.description.split("$")[1]
                return float(price_str)
            except (IndexError, ValueError):
                return None
        return None

    def get_portfolio_value(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, any]:
        """Calculate current portfolio value and returns."""
        investments = db.query(Investment).filter(
            Investment.user_id == user_id
        ).all()
        
        portfolio = {
            "total_value": 0.0,
            "total_cost": 0.0,
            "total_gain_loss": 0.0,
            "investments": []
        }
        
        for inv in investments:
            current_price = self.get_latest_price(db, inv.id)
            if current_price is not None:
                current_value = current_price * inv.quantity
                cost_basis = inv.purchase_price * inv.quantity
                gain_loss = current_value - cost_basis
                gain_loss_percentage = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                
                portfolio["investments"].append({
                    "symbol": inv.symbol,
                    "type": inv.type,
                    "quantity": inv.quantity,
                    "purchase_price": inv.purchase_price,
                    "current_price": current_price,
                    "current_value": current_value,
                    "gain_loss": gain_loss,
                    "gain_loss_percentage": gain_loss_percentage,
                    "currency": inv.currency,
                    "id": inv.id
                })
                
                portfolio["total_value"] += current_value
                portfolio["total_cost"] += cost_basis
                
        portfolio["total_gain_loss"] = portfolio["total_value"] - portfolio["total_cost"]
        portfolio["total_gain_loss_percentage"] = (
            (portfolio["total_gain_loss"] / portfolio["total_cost"]) * 100
            if portfolio["total_cost"] > 0 else 0
        )
        
        return portfolio

    def get_investment_history(
        self,
        db: Session,
        user_id: int,
        investment_type: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """Get investment transaction history."""
        query = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INVESTMENT
        )
        
        if investment_type:
            query = query.filter(Transaction.category == f"{investment_type}_investment")
            
        return [
            {
                "date": tx.date,
                "symbol": tx.description.split()[-1],
                "amount": tx.amount,
                "type": tx.category
            }
            for tx in query.order_by(Transaction.date.desc()).all()
        ]

    def analyze_portfolio_performance(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, any]:
        """Analyze portfolio performance over time."""
        query = db.query(
            func.date_trunc('day', Transaction.date).label('date'),
            func.sum(Transaction.amount).label('daily_value')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INVESTMENT
        )
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
            
        daily_values = query.group_by(text('date')).order_by(text('date')).all()
        
        return {
            "daily_values": [
                {"date": date, "value": float(value)}
                for date, value in daily_values
            ],
            "current_portfolio": self.get_portfolio_value(db, user_id)
        }
