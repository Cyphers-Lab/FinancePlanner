"""Service for managing net worth tracking and calculations."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.models import (
    User, Asset, Debt, Investment, NetWorthSnapshot, 
    NetWorthGoal, AssetType
)

class NetWorthService:
    """Service class for managing net worth tracking and calculations."""

    def __init__(self, db_session: Session):
        """Initialize the service with a database session."""
        self.db = db_session

    def add_asset(self, user_id: int, asset_data: Dict) -> Asset:
        """Add a new asset for a user."""
        asset = Asset(
            user_id=user_id,
            name=asset_data['name'],
            type=AssetType(asset_data['type']),
            value=asset_data['value'],
            description=asset_data.get('description'),
            asset_metadata=asset_data.get('metadata', {}),
            is_liquid=asset_data.get('is_liquid', False),
            is_manual=asset_data.get('is_manual', True),
            institution=asset_data.get('institution'),
            account_number=asset_data.get('account_number')
        )
        self.db.add(asset)
        self.db.commit()
        return asset

    def update_asset(self, asset_id: int, asset_data: Dict) -> Asset:
        """Update an existing asset."""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")

        for key, value in asset_data.items():
            if key == 'type' and value:
                value = AssetType(value)
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        asset.last_updated = datetime.utcnow()
        self.db.commit()
        return asset

    def delete_asset(self, asset_id: int):
        """Delete an asset."""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found")
        
        self.db.delete(asset)
        self.db.commit()

    def get_user_assets(self, user_id: int) -> List[Asset]:
        """Get all assets for a user."""
        return self.db.query(Asset).filter(Asset.user_id == user_id).all()

    def calculate_total_assets(self, user_id: int) -> float:
        """Calculate total value of all assets."""
        # Get manual assets
        assets_total = sum(asset.value for asset in self.get_user_assets(user_id))
        
        # Add investment values
        investments = self.db.query(Investment).filter(Investment.user_id == user_id).all()
        investments_total = sum(inv.quantity * inv.purchase_price for inv in investments)
        
        return assets_total + investments_total

    def calculate_total_liabilities(self, user_id: int) -> float:
        """Calculate total value of all liabilities (debts)."""
        debts = self.db.query(Debt).filter(Debt.user_id == user_id).all()
        return sum(debt.remaining_amount for debt in debts)

    def calculate_net_worth(self, user_id: int) -> Dict:
        """Calculate current net worth and return detailed breakdown."""
        total_assets = self.calculate_total_assets(user_id)
        total_liabilities = self.calculate_total_liabilities(user_id)
        net_worth = total_assets - total_liabilities

        # Create detailed breakdown
        assets = self.get_user_assets(user_id)
        assets_breakdown = {
            asset_type.value: sum(a.value for a in assets if a.type == asset_type)
            for asset_type in AssetType
        }

        investments = self.db.query(Investment).filter(Investment.user_id == user_id).all()
        assets_breakdown['investments'] = sum(inv.quantity * inv.purchase_price for inv in investments)

        debts = self.db.query(Debt).filter(Debt.user_id == user_id).all()
        liabilities_breakdown = {
            debt.name: debt.remaining_amount for debt in debts
        }

        return {
            'net_worth': net_worth,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'assets_breakdown': assets_breakdown,
            'liabilities_breakdown': liabilities_breakdown
        }

    def create_snapshot(self, user_id: int, notes: Optional[str] = None) -> NetWorthSnapshot:
        """Create a new net worth snapshot."""
        calculation = self.calculate_net_worth(user_id)
        
        snapshot = NetWorthSnapshot(
            user_id=user_id,
            total_assets=calculation['total_assets'],
            total_liabilities=calculation['total_liabilities'],
            net_worth=calculation['net_worth'],
            snapshot_data={
                'assets': calculation['assets_breakdown'],
                'liabilities': calculation['liabilities_breakdown']
            },
            notes=notes
        )
        
        self.db.add(snapshot)
        self.db.commit()
        return snapshot

    def get_snapshots(self, user_id: int, limit: Optional[int] = None) -> List[NetWorthSnapshot]:
        """Get historical net worth snapshots."""
        query = self.db.query(NetWorthSnapshot)\
            .filter(NetWorthSnapshot.user_id == user_id)\
            .order_by(desc(NetWorthSnapshot.timestamp))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

    def add_goal(self, user_id: int, goal_data: Dict) -> NetWorthGoal:
        """Add a new net worth goal."""
        current_net_worth = self.calculate_net_worth(user_id)['net_worth']
        
        goal = NetWorthGoal(
            user_id=user_id,
            target_amount=goal_data['target_amount'],
            target_date=goal_data['target_date'],
            start_amount=current_net_worth,
            description=goal_data.get('description')
        )
        
        self.db.add(goal)
        self.db.commit()
        return goal

    def update_goal(self, goal_id: int, goal_data: Dict) -> NetWorthGoal:
        """Update an existing net worth goal."""
        goal = self.db.query(NetWorthGoal).filter(NetWorthGoal.id == goal_id).first()
        if not goal:
            raise ValueError(f"Goal with ID {goal_id} not found")

        for key, value in goal_data.items():
            if hasattr(goal, key):
                setattr(goal, key, value)

        self.db.commit()
        return goal

    def check_goal_progress(self, goal_id: int) -> Dict:
        """Check progress towards a specific net worth goal."""
        goal = self.db.query(NetWorthGoal).filter(NetWorthGoal.id == goal_id).first()
        if not goal:
            raise ValueError(f"Goal with ID {goal_id} not found")

        current_net_worth = self.calculate_net_worth(goal.user_id)['net_worth']
        total_needed = goal.target_amount - goal.start_amount
        progress = current_net_worth - goal.start_amount
        
        if current_net_worth >= goal.target_amount and not goal.is_achieved:
            goal.is_achieved = True
            goal.achieved_date = datetime.utcnow()
            self.db.commit()

        return {
            'goal': goal,
            'current_amount': current_net_worth,
            'progress': progress,
            'total_needed': total_needed,
            'progress_percentage': (progress / total_needed * 100) if total_needed > 0 else 100,
            'remaining_amount': max(0, goal.target_amount - current_net_worth)
        }

    def get_active_goals(self, user_id: int) -> List[NetWorthGoal]:
        """Get all active (unachieved) net worth goals for a user."""
        return self.db.query(NetWorthGoal)\
            .filter(NetWorthGoal.user_id == user_id, NetWorthGoal.is_achieved == False)\
            .order_by(NetWorthGoal.target_date)\
            .all()

    def analyze_net_worth_trend(self, user_id: int, limit: int = 12) -> Dict:
        """Analyze net worth trend over time."""
        snapshots = self.get_snapshots(user_id, limit)
        if not snapshots:
            return {
                'trend': 'insufficient_data',
                'change_amount': 0,
                'change_percentage': 0,
                'average_monthly_change': 0
            }

        current = snapshots[0].net_worth
        oldest = snapshots[-1].net_worth
        change_amount = current - oldest
        change_percentage = (change_amount / oldest * 100) if oldest != 0 else 0
        
        # Calculate average monthly change
        monthly_changes = []
        for i in range(len(snapshots) - 1):
            monthly_change = snapshots[i].net_worth - snapshots[i + 1].net_worth
            monthly_changes.append(monthly_change)
        
        avg_monthly_change = sum(monthly_changes) / len(monthly_changes) if monthly_changes else 0
        
        trend = 'increasing' if change_amount > 0 else 'decreasing' if change_amount < 0 else 'stable'
        
        return {
            'trend': trend,
            'change_amount': change_amount,
            'change_percentage': change_percentage,
            'average_monthly_change': avg_monthly_change
        }
