"""Service for cash flow forecasting and analysis."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import numpy as np
from dateutil.relativedelta import relativedelta

from ..models.models import (
    User, Transaction, RecurringTransaction, CashFlowForecast,
    TransactionType, RecurringFrequency, ForecastType
)

class ForecastService:
    """Service for generating and managing cash flow forecasts."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def detect_recurring_transactions(self, user_id: int, lookback_months: int = 6) -> List[Dict]:
        """Analyze transaction history to detect recurring patterns."""
        lookback_date = datetime.utcnow() - relativedelta(months=lookback_months)
        
        # Get all transactions within lookback period
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= lookback_date
            )
        ).order_by(Transaction.date).all()
        
        # Group transactions by category and type
        transaction_groups = {}
        for tx in transactions:
            key = (tx.category, tx.type, tx.amount)
            if key not in transaction_groups:
                transaction_groups[key] = []
            transaction_groups[key].append(tx)
        
        recurring_patterns = []
        
        for (category, tx_type, amount), group in transaction_groups.items():
            if len(group) < 2:  # Need at least 2 transactions to detect pattern
                continue
                
            # Calculate time differences between consecutive transactions
            intervals = []
            for i in range(1, len(group)):
                delta = group[i].date - group[i-1].date
                intervals.append(delta.days)
            
            if not intervals:
                continue
                
            # Calculate average interval and variance
            avg_interval = sum(intervals) / len(intervals)
            variance = np.var(intervals) if len(intervals) > 1 else 0
            
            # If variance is low enough, consider it a recurring pattern
            if variance < 5 or (variance < 25 and avg_interval > 25):
                frequency = self._determine_frequency(avg_interval)
                if frequency:
                    recurring_patterns.append({
                        'category': category,
                        'type': tx_type,
                        'amount': amount,
                        'frequency': frequency,
                        'confidence': self._calculate_confidence(variance, len(group)),
                        'last_occurrence': group[-1].date,
                        'sample_size': len(group)
                    })
        
        return recurring_patterns
    
    def _determine_frequency(self, avg_interval: float) -> Optional[RecurringFrequency]:
        """Determine the likely frequency of a recurring transaction."""
        if 25 <= avg_interval <= 32:
            return RecurringFrequency.MONTHLY
        elif 13 <= avg_interval <= 15:
            return RecurringFrequency.BIWEEKLY
        elif 6 <= avg_interval <= 8:
            return RecurringFrequency.WEEKLY
        elif 88 <= avg_interval <= 94:
            return RecurringFrequency.QUARTERLY
        elif 360 <= avg_interval <= 370:
            return RecurringFrequency.ANNUALLY
        return None
    
    def _calculate_confidence(self, variance: float, sample_size: int) -> float:
        """Calculate confidence score for a recurring pattern."""
        base_score = 1.0 - min(variance / 100, 0.5)  # Variance penalty
        sample_bonus = min(sample_size / 12, 0.5)    # Bonus for more samples
        return min(base_score + sample_bonus, 1.0)
    
    def create_recurring_transaction(
        self, user_id: int, name: str, tx_type: TransactionType,
        amount: float, category: str, frequency: RecurringFrequency,
        start_date: datetime, end_date: Optional[datetime] = None
    ) -> RecurringTransaction:
        """Create a new recurring transaction."""
        next_occurrence = self._calculate_next_occurrence(start_date, frequency)
        
        recurring_tx = RecurringTransaction(
            user_id=user_id,
            name=name,
            type=tx_type,
            amount=amount,
            category=category,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            next_occurrence=next_occurrence
        )
        
        self.db.add(recurring_tx)
        self.db.commit()
        return recurring_tx
    
    def _calculate_next_occurrence(
        self, start_date: datetime, frequency: RecurringFrequency,
        from_date: Optional[datetime] = None
    ) -> datetime:
        """Calculate the next occurrence date based on frequency."""
        if from_date is None:
            from_date = datetime.utcnow()
        
        if from_date < start_date:
            return start_date
            
        delta_mapping = {
            RecurringFrequency.DAILY: timedelta(days=1),
            RecurringFrequency.WEEKLY: timedelta(weeks=1),
            RecurringFrequency.BIWEEKLY: timedelta(weeks=2),
            RecurringFrequency.MONTHLY: relativedelta(months=1),
            RecurringFrequency.QUARTERLY: relativedelta(months=3),
            RecurringFrequency.ANNUALLY: relativedelta(years=1)
        }
        
        delta = delta_mapping[frequency]
        next_date = start_date
        
        while next_date <= from_date:
            if isinstance(delta, relativedelta):
                next_date += delta
            else:
                next_date = next_date + delta
                
        return next_date
    
    def generate_forecast(
        self, user_id: int, forecast_type: ForecastType,
        start_date: Optional[datetime] = None,
        periods: int = 12
    ) -> CashFlowForecast:
        """Generate a cash flow forecast for the specified period."""
        if start_date is None:
            start_date = datetime.utcnow()
        
        # Calculate end date based on forecast type and periods
        if forecast_type == ForecastType.WEEKLY:
            end_date = start_date + timedelta(weeks=periods)
            interval = timedelta(weeks=1)
        elif forecast_type == ForecastType.MONTHLY:
            end_date = start_date + relativedelta(months=periods)
            interval = relativedelta(months=1)
        else:  # QUARTERLY
            end_date = start_date + relativedelta(months=periods*3)
            interval = relativedelta(months=3)
        
        # Get all active recurring transactions
        recurring_txs = self.db.query(RecurringTransaction).filter(
            and_(
                RecurringTransaction.user_id == user_id,
                RecurringTransaction.is_active == True,
                or_(
                    RecurringTransaction.end_date == None,
                    RecurringTransaction.end_date >= start_date
                )
            )
        ).all()
        
        # Initialize forecast data structure
        forecast_data = []
        current_date = start_date
        
        while current_date <= end_date:
            period_end = current_date + interval
            
            # Calculate expected transactions for this period
            period_transactions = []
            period_total = 0.0
            
            for rtx in recurring_txs:
                next_date = rtx.next_occurrence
                while next_date < period_end:
                    if rtx.end_date and next_date > rtx.end_date:
                        break
                        
                    period_transactions.append({
                        'date': next_date.isoformat(),
                        'name': rtx.name,
                        'type': rtx.type.value,
                        'amount': rtx.amount,
                        'category': rtx.category
                    })
                    
                    amount = rtx.amount if rtx.type == TransactionType.INCOME else -rtx.amount
                    period_total += amount
                    
                    next_date = self._calculate_next_occurrence(
                        rtx.start_date, rtx.frequency, next_date
                    )
            
            forecast_data.append({
                'start_date': current_date.isoformat(),
                'end_date': period_end.isoformat(),
                'transactions': period_transactions,
                'net_cash_flow': period_total
            })
            
            current_date = period_end
        
        # Create and save forecast
        forecast = CashFlowForecast(
            user_id=user_id,
            forecast_type=forecast_type,
            start_date=start_date,
            end_date=end_date,
            forecast_data=forecast_data,
            forecast_metadata={
                'recurring_transactions_count': len(recurring_txs),
                'generated_at': datetime.utcnow().isoformat()
            }
        )
        
        self.db.add(forecast)
        self.db.commit()
        return forecast
    
    def get_latest_forecast(
        self, user_id: int, forecast_type: ForecastType
    ) -> Optional[CashFlowForecast]:
        """Get the most recent forecast for the user."""
        return self.db.query(CashFlowForecast).filter(
            and_(
                CashFlowForecast.user_id == user_id,
                CashFlowForecast.forecast_type == forecast_type
            )
        ).order_by(CashFlowForecast.created_at.desc()).first()
    
    def analyze_forecast_accuracy(
        self, forecast: CashFlowForecast
    ) -> Tuple[float, Dict]:
        """Analyze the accuracy of a past forecast compared to actual results."""
        if forecast.end_date > datetime.utcnow():
            return None, {}  # Cannot analyze accuracy of future forecasts
            
        actual_transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == forecast.user_id,
                Transaction.date >= forecast.start_date,
                Transaction.date <= forecast.end_date
            )
        ).all()
        
        # Group actual transactions by period
        actual_by_period = {}
        for tx in actual_transactions:
            period_key = self._get_period_key(tx.date, forecast.forecast_type)
            if period_key not in actual_by_period:
                actual_by_period[period_key] = 0.0
            amount = tx.amount if tx.type == TransactionType.INCOME else -tx.amount
            actual_by_period[period_key] += amount
        
        # Compare forecast to actuals
        total_error = 0.0
        comparison_data = []
        
        for period in forecast.forecast_data:
            period_start = datetime.fromisoformat(period['start_date'])
            period_key = self._get_period_key(period_start, forecast.forecast_type)
            
            forecast_amount = period['net_cash_flow']
            actual_amount = actual_by_period.get(period_key, 0.0)
            
            error = abs(forecast_amount - actual_amount)
            total_error += error
            
            comparison_data.append({
                'period_start': period['start_date'],
                'period_end': period['end_date'],
                'forecasted': forecast_amount,
                'actual': actual_amount,
                'error': error,
                'error_percentage': (error / abs(forecast_amount) * 100) if forecast_amount != 0 else 0
            })
        
        # Calculate overall accuracy score (0-1)
        total_forecast = sum(abs(p['net_cash_flow']) for p in forecast.forecast_data)
        accuracy_score = 1.0 - (total_error / total_forecast) if total_forecast > 0 else 0
        
        return accuracy_score, {
            'period_comparisons': comparison_data,
            'average_error_percentage': sum(d['error_percentage'] for d in comparison_data) / len(comparison_data)
        }
    
    def _get_period_key(self, date: datetime, forecast_type: ForecastType) -> str:
        """Generate a consistent key for grouping transactions by forecast period."""
        if forecast_type == ForecastType.WEEKLY:
            return date.strftime('%Y-W%W')
        elif forecast_type == ForecastType.MONTHLY:
            return date.strftime('%Y-%m')
        else:  # QUARTERLY
            quarter = (date.month - 1) // 3 + 1
            return f"{date.year}-Q{quarter}"
