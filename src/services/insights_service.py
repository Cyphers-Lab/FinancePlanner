"""Service for generating and managing financial insights."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from ..models.models import (
    User, Transaction, Budget, SavingsGoal, Debt, Investment,
    Insight, InsightType, InsightPriority, UserPreferences
)

class InsightsService:
    """Service class for managing financial insights and recommendations."""

    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db = db_session

    def get_user_insights(
        self, 
        user_id: int, 
        insight_type: Optional[InsightType] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get insights for a user, optionally filtered by type."""
        query = self.db.query(Insight).filter(Insight.user_id == user_id)
        
        if insight_type:
            query = query.filter(Insight.type == insight_type)
        
        insights = (query.order_by(Insight.priority.desc(), Insight.created_at.desc())
                   .limit(limit)
                   .all())
        
        return [self._format_insight(insight) for insight in insights]

    def generate_insights(self, user_id: int) -> List[Dict]:
        """Generate new insights based on user's financial data."""
        user = self.db.query(User).get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        preferences = (self.db.query(UserPreferences)
                     .filter_by(user_id=user_id)
                     .first())
        
        if not preferences:
            preferences = UserPreferences(user_id=user_id)
            self.db.add(preferences)
            self.db.commit()

        insights = []
        
        if preferences.insight_preferences.get('spending_patterns', True):
            insights.extend(self._analyze_spending_patterns(user))
        
        if preferences.insight_preferences.get('savings_opportunities', True):
            insights.extend(self._find_savings_opportunities(user))
        
        if preferences.insight_preferences.get('investment_suggestions', True):
            insights.extend(self._generate_investment_suggestions(user))
        
        if preferences.insight_preferences.get('budget_alerts', True):
            insights.extend(self._check_budget_status(user))
        
        if preferences.insight_preferences.get('debt_management', True):
            insights.extend(self._analyze_debt_situation(user))

        # Save the generated insights to the database
        for insight_data in insights:
            insight = Insight(
                user_id=user_id,
                type=InsightType(insight_data['type']),
                priority=InsightPriority(insight_data['priority']),
                title=insight_data['title'],
                description=insight_data['description'],
                recommendation=insight_data['recommendation'],
                insight_metadata=insight_data.get('insight_metadata', {}),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30)  # Insights expire after 30 days
            )
            self.db.add(insight)
        
        self.db.commit()
        return self.get_user_insights(user_id)  # Return the newly saved insights

    def _analyze_spending_patterns(self, user: User) -> List[Dict]:
        """Analyze user spending patterns for unusual activity or trends."""
        insights = []
        
        # Get transactions from last 3 months
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        transactions = (self.db.query(Transaction)
                      .filter(and_(
                          Transaction.user_id == user.id,
                          Transaction.date >= three_months_ago,
                          Transaction.type == 'expense'
                      ))
                      .all())

        # Group transactions by category
        category_totals = {}
        for transaction in transactions:
            if transaction.category not in category_totals:
                category_totals[transaction.category] = []
            category_totals[transaction.category].append(transaction.amount)

        # Analyze each category for unusual patterns
        for category, amounts in category_totals.items():
            avg_amount = sum(amounts) / len(amounts)
            max_amount = max(amounts)
            
            if max_amount > avg_amount * 1.5:  # Significant increase
                insights.append({
                    'type': InsightType.SPENDING_PATTERN.value,
                    'priority': InsightPriority.HIGH.value,
                    'title': f'Unusual Spending in {category}',
                    'description': (f'Your spending in {category} has increased '
                                  f'significantly above your average.'),
                    'recommendation': ('Consider reviewing your spending in this '
                                     'category and setting a budget if needed.'),
                    'insight_metadata': {
                        'category': category,
                        'average_amount': avg_amount,
                        'max_amount': max_amount
                    }
                })

        return insights

    def _find_savings_opportunities(self, user: User) -> List[Dict]:
        """Identify potential savings opportunities."""
        insights = []
        
        # Get monthly income
        monthly_income = (self.db.query(func.sum(Transaction.amount))
                        .filter(and_(
                            Transaction.user_id == user.id,
                            Transaction.type == 'income',
                            Transaction.date >= datetime.utcnow() - timedelta(days=30)
                        ))
                        .scalar() or 0)

        # Get monthly expenses
        monthly_expenses = (self.db.query(func.sum(Transaction.amount))
                          .filter(and_(
                              Transaction.user_id == user.id,
                              Transaction.type == 'expense',
                              Transaction.date >= datetime.utcnow() - timedelta(days=30)
                          ))
                          .scalar() or 0)

        # Calculate savings rate
        if monthly_income > 0:
            savings_rate = (monthly_income - monthly_expenses) / monthly_income
            
            if savings_rate < 0.2:  # Less than 20% savings
                insights.append({
                    'type': InsightType.SAVINGS_OPPORTUNITY.value,
                    'priority': InsightPriority.HIGH.value,
                    'title': 'Low Savings Rate Detected',
                    'description': ('Your current savings rate is below the '
                                  'recommended 20% of income.'),
                    'recommendation': ('Try to identify non-essential expenses that '
                                     'could be reduced to increase your savings rate.'),
                    'insight_metadata': {
                        'current_rate': savings_rate,
                        'target_rate': 0.2,
                        'monthly_income': monthly_income
                    }
                })

        return insights

    def _generate_investment_suggestions(self, user: User) -> List[Dict]:
        """Generate investment suggestions based on user's profile."""
        insights = []
        
        preferences = self.db.query(UserPreferences).filter_by(user_id=user.id).first()
        if not preferences:
            return insights

        # Get total investment value
        investments = self.db.query(Investment).filter_by(user_id=user.id).all()
        total_invested = sum(inv.quantity * inv.purchase_price for inv in investments)

        # Get monthly income
        monthly_income = (self.db.query(func.sum(Transaction.amount))
                        .filter(and_(
                            Transaction.user_id == user.id,
                            Transaction.type == 'income',
                            Transaction.date >= datetime.utcnow() - timedelta(days=30)
                        ))
                        .scalar() or 0)

        if total_invested < monthly_income * 6:  # Less than 6 months income invested
            suggestion = {
                'conservative': 'Consider low-risk index funds or bonds',
                'moderate': 'Consider a mix of index funds and individual stocks',
                'aggressive': 'Consider growth stocks and emerging market funds'
            }[preferences.risk_tolerance]

            insights.append({
                'type': InsightType.INVESTMENT_SUGGESTION.value,
                'priority': InsightPriority.MEDIUM.value,
                'title': 'Investment Opportunity Identified',
                'description': ('Your investment portfolio could benefit from '
                              'additional diversification.'),
                'recommendation': suggestion,
                'insight_metadata': {
                    'current_investment': total_invested,
                    'monthly_income': monthly_income,
                    'risk_tolerance': preferences.risk_tolerance
                }
            })

        return insights

    def _check_budget_status(self, user: User) -> List[Dict]:
        """Check budget status and generate alerts if needed."""
        insights = []
        
        current_month = datetime.utcnow().replace(day=1)
        budgets = self.db.query(Budget).filter_by(user_id=user.id).all()

        for budget in budgets:
            spent = (self.db.query(func.sum(Transaction.amount))
                    .filter(and_(
                        Transaction.budget_id == budget.id,
                        Transaction.date >= current_month
                    ))
                    .scalar() or 0)

            if spent >= budget.amount * budget.alert_threshold:
                insights.append({
                    'type': InsightType.BUDGET_ALERT.value,
                    'priority': InsightPriority.URGENT.value,
                    'title': f'Budget Alert: {budget.category}',
                    'description': (f'You have used {(spent/budget.amount)*100:.1f}% '
                                  f'of your {budget.category} budget.'),
                    'recommendation': ('Consider reducing spending in this category '
                                     'for the rest of the month.'),
                    'insight_metadata': {
                        'category': budget.category,
                        'budget_amount': budget.amount,
                        'spent_amount': spent,
                        'remaining': budget.amount - spent
                    }
                })

        return insights

    def _analyze_debt_situation(self, user: User) -> List[Dict]:
        """Analyze debt situation and provide management suggestions."""
        insights = []
        
        debts = self.db.query(Debt).filter_by(user_id=user.id).all()
        if not debts:
            return insights

        # Sort debts by interest rate
        high_interest_debts = [d for d in debts if d.interest_rate > 10]
        
        if high_interest_debts:
            insights.append({
                'type': InsightType.DEBT_MANAGEMENT.value,
                'priority': InsightPriority.HIGH.value,
                'title': 'High Interest Debt Alert',
                'description': ('You have debt with high interest rates that '
                              'should be prioritized for repayment.'),
                'recommendation': ('Consider using the debt avalanche method: '
                                 'pay minimum on all debts but put extra money '
                                 'toward the highest interest debt first.'),
                'insight_metadata': {
                    'high_interest_debts': [
                        {
                            'name': d.name,
                            'rate': d.interest_rate,
                            'amount': d.remaining_amount
                        }
                        for d in high_interest_debts
                    ]
                }
            })

        return insights

    def _format_insight(self, insight: Insight) -> Dict:
        """Format insight object into dictionary."""
        return {
            'id': insight.id,
            'type': insight.type.value,
            'priority': insight.priority.value,
            'title': insight.title,
            'description': insight.description,
            'recommendation': insight.recommendation,
            'insight_metadata': insight.insight_metadata,
            'created_at': insight.created_at.isoformat(),
            'expires_at': insight.expires_at.isoformat() if insight.expires_at else None,
            'is_read': insight.is_read,
            'is_acted_upon': insight.is_acted_upon,
            'feedback_rating': insight.feedback_rating
        }

    def mark_insight_read(self, insight_id: int, user_id: int) -> None:
        """Mark an insight as read."""
        insight = (self.db.query(Insight)
                  .filter(and_(
                      Insight.id == insight_id,
                      Insight.user_id == user_id
                  ))
                  .first())
        
        if insight:
            insight.is_read = True
            self.db.commit()

    def mark_insight_acted_upon(self, insight_id: int, user_id: int) -> None:
        """Mark an insight as acted upon."""
        insight = (self.db.query(Insight)
                  .filter(and_(
                      Insight.id == insight_id,
                      Insight.user_id == user_id
                  ))
                  .first())
        
        if insight:
            insight.is_acted_upon = True
            self.db.commit()

    def rate_insight(self, insight_id: int, user_id: int, rating: int) -> None:
        """Rate an insight's usefulness."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        insight = (self.db.query(Insight)
                  .filter(and_(
                      Insight.id == insight_id,
                      Insight.user_id == user_id
                  ))
                  .first())
        
        if insight:
            insight.feedback_rating = rating
            self.db.commit()
