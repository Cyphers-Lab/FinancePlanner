"""Savings goal management service for the Financial Planner application."""
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.models import SavingsGoal, Transaction, TransactionType, SavingsGoalPriority, SavingsGoalType

class SavingsService:
    """Service for managing savings goals and their progress."""

    def create_goal(
        self,
        db: Session,
        user_id: int,
        name: str,
        target_amount: float,
        description: Optional[str] = None,
        target_date: Optional[datetime] = None,
        priority: SavingsGoalPriority = SavingsGoalPriority.MEDIUM,
        goal_type: SavingsGoalType = SavingsGoalType.ONE_TIME,
        allocation_rules: Optional[Dict[str, Any]] = None,
        recurring_period: Optional[str] = None,
        monthly_expenses: Optional[float] = None,
        months_coverage: Optional[float] = None,
        critical_threshold: Optional[float] = None
    ) -> SavingsGoal:
        """Create a new savings goal or emergency fund."""
        goal = SavingsGoal(
            user_id=user_id,
            name=name,
            description=description,
            target_amount=target_amount,
            target_date=target_date,
            priority=priority,
            goal_type=goal_type,
            allocation_rules=allocation_rules,
            recurring_period=recurring_period,
            monthly_expenses=monthly_expenses if goal_type == SavingsGoalType.EMERGENCY_FUND else None,
            months_coverage=months_coverage if goal_type == SavingsGoalType.EMERGENCY_FUND else None,
            critical_threshold=critical_threshold if goal_type == SavingsGoalType.EMERGENCY_FUND else None
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    def get_user_goals(
        self,
        db: Session,
        user_id: int,
        include_completed: bool = False
    ) -> List[SavingsGoal]:
        """Get all savings goals for a user."""
        query = db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id)
        if not include_completed:
            query = query.filter(SavingsGoal.current_amount < SavingsGoal.target_amount)
        return query.order_by(SavingsGoal.priority.desc()).all()

    def update_goal(
        self,
        db: Session,
        goal_id: int,
        target_amount: Optional[float] = None,
        target_date: Optional[datetime] = None,
        priority: Optional[SavingsGoalPriority] = None,
        allocation_rules: Optional[Dict[str, Any]] = None,
        is_paused: Optional[bool] = None
    ) -> SavingsGoal:
        """Update an existing savings goal."""
        goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
        if not goal:
            raise ValueError("Goal not found")

        if target_amount is not None:
            goal.target_amount = target_amount
        if target_date is not None:
            goal.target_date = target_date
        if priority is not None:
            goal.priority = priority
        if allocation_rules is not None:
            goal.allocation_rules = allocation_rules
        if is_paused is not None:
            goal.is_paused = is_paused

        db.commit()
        db.refresh(goal)
        return goal

    def delete_goal(self, db: Session, goal_id: int) -> bool:
        """Delete a savings goal."""
        goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
        if not goal:
            return False

        db.delete(goal)
        db.commit()
        return True

    def allocate_income(
        self,
        db: Session,
        user_id: int,
        income_amount: float,
        income_transaction_id: int
    ) -> List[Dict[str, Any]]:
        """Allocate income to savings goals based on their rules."""
        goals = self.get_user_goals(db, user_id)
        allocations = []

        # Sort goals by priority
        goals.sort(key=lambda g: (
            g.is_paused,  # Paused goals last
            -g.priority.value,  # Higher priority first
            g.target_date or datetime.max  # Earlier deadlines first
        ))

        remaining_amount = income_amount
        for goal in goals:
            if goal.is_paused or remaining_amount <= 0:
                continue

            if not goal.allocation_rules:
                continue

            # Calculate allocation amount based on rules
            allocation_amount = 0
            if "percentage" in goal.allocation_rules:
                allocation_amount = income_amount * (goal.allocation_rules["percentage"] / 100)
            elif "fixed_amount" in goal.allocation_rules:
                allocation_amount = goal.allocation_rules["fixed_amount"]

            # Adjust for remaining amount and goal target
            remaining_to_target = goal.target_amount - goal.current_amount
            allocation_amount = min(allocation_amount, remaining_to_target, remaining_amount)

            if allocation_amount > 0:
                # Create transaction for this allocation
                transaction = Transaction(
                    user_id=user_id,
                    savings_goal_id=goal.id,
                    type=TransactionType.SAVINGS,
                    amount=allocation_amount,
                    description=f"Automatic allocation to {goal.name}",
                    category="Savings",
                    date=datetime.utcnow()
                )
                db.add(transaction)

                # Update goal progress
                goal.current_amount += allocation_amount
                remaining_amount -= allocation_amount

                allocations.append({
                    "goal_id": goal.id,
                    "goal_name": goal.name,
                    "amount": allocation_amount
                })

        db.commit()
        return allocations

    def get_goal_progress(
        self,
        db: Session,
        goal_id: int
    ) -> Dict[str, Any]:
        """Get detailed progress information for a goal."""
        goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()
        if not goal:
            raise ValueError("Goal not found")

        progress_percentage = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        
        # Calculate monthly average contribution
        monthly_avg = db.query(func.avg(Transaction.amount))\
            .filter(
                Transaction.savings_goal_id == goal_id,
                Transaction.type == TransactionType.SAVINGS
            ).scalar() or 0

        # Get recent transactions
        recent_transactions = db.query(Transaction)\
            .filter(
                Transaction.savings_goal_id == goal_id,
                Transaction.type == TransactionType.SAVINGS
            )\
            .order_by(Transaction.date.desc())\
            .limit(5)\
            .all()

        return {
            "goal": goal,
            "progress_percentage": progress_percentage,
            "monthly_average": monthly_avg,
            "recent_transactions": recent_transactions,
            "remaining_amount": goal.target_amount - goal.current_amount,
            "is_completed": goal.current_amount >= goal.target_amount
        }

    def check_goal_alerts(
        self,
        db: Session,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Check all goals for alerts (behind schedule, nearing deadline, etc.)."""
        goals = self.get_user_goals(db, user_id)
        alerts = []

        for goal in goals:
            if goal.is_paused:
                continue

            if goal.target_date:
                days_remaining = (goal.target_date - datetime.utcnow()).days
                if days_remaining <= 0:
                    alerts.append({
                        "goal_id": goal.id,
                        "goal_name": goal.name,
                        "type": "deadline_passed",
                        "message": f"Deadline passed for goal: {goal.name}"
                    })
                elif days_remaining <= 30:
                    alerts.append({
                        "goal_id": goal.id,
                        "goal_name": goal.name,
                        "type": "deadline_approaching",
                        "message": f"Only {days_remaining} days left to reach goal: {goal.name}"
                    })

            # Check if goal is behind schedule
            if goal.target_date:
                total_days = (goal.target_date - goal.start_date).days
                days_elapsed = (datetime.utcnow() - goal.start_date).days
                expected_progress = (days_elapsed / total_days) * goal.target_amount
                if goal.current_amount < expected_progress * 0.8:  # More than 20% behind schedule
                    alerts.append({
                        "goal_id": goal.id,
                        "goal_name": goal.name,
                        "type": "behind_schedule",
                        "message": f"Goal {goal.name} is significantly behind schedule"
                    })

        return alerts

    def create_emergency_fund(
        self,
        db: Session,
        user_id: int,
        monthly_expenses: float,
        months_coverage: float = 6.0,
        critical_threshold: float = 0.5,
        allocation_rules: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> SavingsGoal:
        """Create an emergency fund goal."""
        target_amount = monthly_expenses * months_coverage
        name = "Emergency Fund"
        
        return self.create_goal(
            db=db,
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            description=description or "Emergency fund for unexpected expenses",
            priority=SavingsGoalPriority.CRITICAL,
            goal_type=SavingsGoalType.EMERGENCY_FUND,
            allocation_rules=allocation_rules,
            monthly_expenses=monthly_expenses,
            months_coverage=months_coverage,
            critical_threshold=critical_threshold
        )

    def update_emergency_fund(
        self,
        db: Session,
        goal_id: int,
        monthly_expenses: Optional[float] = None,
        months_coverage: Optional[float] = None,
        critical_threshold: Optional[float] = None
    ) -> SavingsGoal:
        """Update emergency fund parameters and recalculate target amount."""
        goal = db.query(SavingsGoal).filter(
            SavingsGoal.id == goal_id,
            SavingsGoal.goal_type == SavingsGoalType.EMERGENCY_FUND
        ).first()
        
        if not goal:
            raise ValueError("Emergency fund not found")

        if monthly_expenses is not None:
            goal.monthly_expenses = monthly_expenses
            goal.target_amount = monthly_expenses * (months_coverage or goal.months_coverage)
        
        if months_coverage is not None:
            goal.months_coverage = months_coverage
            goal.target_amount = (monthly_expenses or goal.monthly_expenses) * months_coverage
        
        if critical_threshold is not None:
            goal.critical_threshold = critical_threshold

        db.commit()
        db.refresh(goal)
        return goal

    def record_emergency_withdrawal(
        self,
        db: Session,
        goal_id: int,
        amount: float,
        description: str
    ) -> Dict[str, Any]:
        """Record a withdrawal from the emergency fund and create necessary alerts."""
        goal = db.query(SavingsGoal).filter(
            SavingsGoal.id == goal_id,
            SavingsGoalType.EMERGENCY_FUND
        ).first()
        
        if not goal:
            raise ValueError("Emergency fund not found")
            
        if amount > goal.current_amount:
            raise ValueError("Withdrawal amount exceeds available funds")

        # Create withdrawal transaction
        transaction = Transaction(
            user_id=goal.user_id,
            savings_goal_id=goal.id,
            type=TransactionType.EXPENSE,
            amount=-amount,
            description=description,
            category="Emergency Withdrawal",
            date=datetime.utcnow()
        )
        db.add(transaction)

        # Update fund balance
        goal.current_amount -= amount
        goal.last_withdrawal = datetime.utcnow()

        # Create alert for the withdrawal
        alert = EmergencyFundAlert(
            user_id=goal.user_id,
            savings_goal_id=goal.id,
            alert_type="withdrawal_made",
            current_balance=goal.current_amount,
            threshold_value=None
        )
        db.add(alert)

        # Check if balance is below critical threshold
        if goal.current_amount < (goal.target_amount * goal.critical_threshold):
            threshold_alert = EmergencyFundAlert(
                user_id=goal.user_id,
                savings_goal_id=goal.id,
                alert_type="threshold_breach",
                current_balance=goal.current_amount,
                threshold_value=goal.critical_threshold
            )
            db.add(threshold_alert)

        db.commit()
        
        return {
            "transaction": transaction,
            "new_balance": goal.current_amount,
            "months_coverage_remaining": goal.current_amount / goal.monthly_expenses if goal.monthly_expenses > 0 else 0
        }

    def check_emergency_fund_status(
        self,
        db: Session,
        goal_id: int
    ) -> Dict[str, Any]:
        """Get detailed status of an emergency fund."""
        goal = db.query(SavingsGoal).filter(
            SavingsGoal.id == goal_id,
            SavingsGoalType.EMERGENCY_FUND
        ).first()
        
        if not goal:
            raise ValueError("Emergency fund not found")

        months_coverage = goal.current_amount / goal.monthly_expenses if goal.monthly_expenses > 0 else 0
        target_months = goal.months_coverage
        
        return {
            "current_balance": goal.current_amount,
            "target_amount": goal.target_amount,
            "monthly_expenses": goal.monthly_expenses,
            "months_coverage_current": months_coverage,
            "months_coverage_target": target_months,
            "last_withdrawal": goal.last_withdrawal,
            "is_below_critical": goal.current_amount < (goal.target_amount * goal.critical_threshold),
            "critical_threshold": goal.critical_threshold,
            "progress_percentage": (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        }
