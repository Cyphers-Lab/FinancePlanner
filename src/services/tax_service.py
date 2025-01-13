"""Service for handling tax-related operations."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.models import (
    User, Transaction, TaxProfile, TaxReport, 
    EmploymentType, TaxCategory, TransactionType
)

class TaxService:
    """Service class for tax-related operations."""
    
    def __init__(self, db_session: Session):
        """Initialize the tax service with a database session."""
        self.db = db_session

    def create_tax_profile(
        self, 
        user_id: int,
        employment_type: EmploymentType,
        tax_year: int,
        filing_status: str,
        tax_id: Optional[str] = None,
        withholding_rate: Optional[float] = None,
        estimated_tax_rate: Optional[float] = None,
        deduction_preferences: Optional[Dict] = None,
        custom_tax_brackets: Optional[Dict] = None
    ) -> TaxProfile:
        """Create or update a tax profile for a user."""
        # Check for existing profile for the tax year
        existing_profile = self.db.query(TaxProfile).filter(
            and_(TaxProfile.user_id == user_id, TaxProfile.tax_year == tax_year)
        ).first()

        if existing_profile:
            # Update existing profile
            existing_profile.employment_type = employment_type
            existing_profile.filing_status = filing_status
            existing_profile.tax_id = tax_id
            existing_profile.withholding_rate = withholding_rate
            existing_profile.estimated_tax_rate = estimated_tax_rate
            existing_profile.deduction_preferences = deduction_preferences
            existing_profile.custom_tax_brackets = custom_tax_brackets
            existing_profile.updated_at = datetime.utcnow()
            profile = existing_profile
        else:
            # Create new profile
            profile = TaxProfile(
                user_id=user_id,
                employment_type=employment_type,
                tax_year=tax_year,
                filing_status=filing_status,
                tax_id=tax_id,
                withholding_rate=withholding_rate,
                estimated_tax_rate=estimated_tax_rate,
                deduction_preferences=deduction_preferences,
                custom_tax_brackets=custom_tax_brackets
            )
            self.db.add(profile)

        self.db.commit()
        return profile

    def get_tax_profile(self, user_id: int, tax_year: int) -> Optional[TaxProfile]:
        """Get a user's tax profile for a specific year."""
        return self.db.query(TaxProfile).filter(
            and_(TaxProfile.user_id == user_id, TaxProfile.tax_year == tax_year)
        ).first()

    def categorize_transaction(
        self,
        transaction_id: int,
        tax_category: TaxCategory,
        tax_deductible_amount: Optional[float] = None,
        tax_notes: Optional[str] = None
    ) -> Transaction:
        """Categorize a transaction for tax purposes."""
        transaction = self.db.query(Transaction).get(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")

        transaction.tax_category = tax_category
        transaction.tax_deductible_amount = tax_deductible_amount
        transaction.tax_notes = tax_notes

        self.db.commit()
        return transaction

    def get_tax_summary(self, user_id: int, tax_year: int) -> Dict:
        """Generate a tax summary for a specific year."""
        # Get all transactions for the year
        start_date = datetime(tax_year, 1, 1)
        end_date = datetime(tax_year + 1, 1, 1)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date < end_date
            )
        ).all()

        # Initialize summary
        summary = {
            "total_income": 0.0,
            "total_deductible_expenses": 0.0,
            "total_non_deductible_expenses": 0.0,
            "tax_credits": 0.0,
            "exempt_income": 0.0,
            "categorized_deductions": {},
            "uncategorized_transactions": []
        }

        # Process transactions
        for transaction in transactions:
            if transaction.type == TransactionType.INCOME:
                if transaction.tax_category == TaxCategory.EXEMPT:
                    summary["exempt_income"] += transaction.amount
                else:
                    summary["total_income"] += transaction.amount
            
            elif transaction.type == TransactionType.EXPENSE:
                if not transaction.tax_category:
                    summary["uncategorized_transactions"].append({
                        "id": transaction.id,
                        "amount": transaction.amount,
                        "description": transaction.description,
                        "category": transaction.category
                    })
                elif transaction.tax_category == TaxCategory.DEDUCTIBLE:
                    deductible_amount = (
                        transaction.tax_deductible_amount or transaction.amount
                    )
                    summary["total_deductible_expenses"] += deductible_amount
                    
                    # Categorize deductions
                    if transaction.category not in summary["categorized_deductions"]:
                        summary["categorized_deductions"][transaction.category] = 0
                    summary["categorized_deductions"][transaction.category] += deductible_amount
                
                elif transaction.tax_category == TaxCategory.TAX_CREDIT:
                    summary["tax_credits"] += transaction.amount
                else:
                    summary["total_non_deductible_expenses"] += transaction.amount

        return summary

    def generate_tax_report(self, user_id: int, tax_year: int) -> TaxReport:
        """Generate a detailed tax report."""
        # Get tax profile and summary
        profile = self.get_tax_profile(user_id, tax_year)
        if not profile:
            raise ValueError(f"No tax profile found for year {tax_year}")

        summary = self.get_tax_summary(user_id, tax_year)
        
        # Calculate estimated tax liability
        taxable_income = summary["total_income"] - summary["total_deductible_expenses"]
        estimated_tax = 0.0
        
        if profile.employment_type == EmploymentType.PAYEE and profile.withholding_rate:
            estimated_tax = taxable_income * profile.withholding_rate
        elif profile.estimated_tax_rate:
            estimated_tax = taxable_income * profile.estimated_tax_rate
        else:
            # Use custom tax brackets or default calculation
            if profile.custom_tax_brackets:
                # Custom tax bracket calculation logic
                brackets = profile.custom_tax_brackets
                for bracket in sorted(brackets.items(), key=lambda x: float(x[0])):
                    threshold = float(bracket[0])
                    rate = float(bracket[1])
                    if taxable_income > threshold:
                        estimated_tax += (taxable_income - threshold) * rate
            else:
                # Simple default calculation (should be replaced with actual tax brackets)
                estimated_tax = taxable_income * 0.25  # Default 25% rate

        # Create tax report
        report = TaxReport(
            user_id=user_id,
            tax_year=tax_year,
            generated_date=datetime.utcnow(),
            total_income=summary["total_income"],
            total_deductions=summary["total_deductible_expenses"],
            estimated_tax_liability=estimated_tax,
            report_data={
                "summary": summary,
                "profile": {
                    "employment_type": profile.employment_type.value,
                    "filing_status": profile.filing_status
                },
                "calculations": {
                    "taxable_income": taxable_income,
                    "estimated_tax": estimated_tax,
                    "tax_credits": summary["tax_credits"],
                    "final_tax_liability": max(0, estimated_tax - summary["tax_credits"])
                }
            }
        )

        self.db.add(report)
        self.db.commit()
        return report

    def get_tax_reports(self, user_id: int) -> List[TaxReport]:
        """Get all tax reports for a user."""
        return self.db.query(TaxReport).filter(
            TaxReport.user_id == user_id
        ).order_by(TaxReport.tax_year.desc()).all()

    def get_uncategorized_transactions(
        self, user_id: int, tax_year: int
    ) -> List[Transaction]:
        """Get transactions that haven't been categorized for tax purposes."""
        start_date = datetime(tax_year, 1, 1)
        end_date = datetime(tax_year + 1, 1, 1)
        
        return self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date < end_date,
                Transaction.tax_category.is_(None)
            )
        ).all()

    def suggest_tax_categories(self, transaction: Transaction) -> List[Dict]:
        """Suggest possible tax categories for a transaction based on its properties."""
        suggestions = []
        
        # Common deductible categories
        deductible_keywords = {
            "office": ["office supplies", "computer", "software", "printer"],
            "travel": ["flight", "hotel", "taxi", "uber", "lyft"],
            "education": ["course", "training", "workshop", "seminar"],
            "medical": ["doctor", "hospital", "medicine", "pharmacy"],
            "charity": ["donation", "charitable", "nonprofit"],
            "business": ["client", "meeting", "advertising", "marketing"]
        }

        description_lower = transaction.description.lower()
        category_lower = transaction.category.lower()

        for category, keywords in deductible_keywords.items():
            if any(keyword in description_lower or keyword in category_lower 
                  for keyword in keywords):
                suggestions.append({
                    "category": TaxCategory.DEDUCTIBLE,
                    "confidence": 0.8,
                    "reason": f"Matches common {category} expense pattern",
                    "suggested_notes": f"Potential {category} deduction"
                })

        # Add more suggestion logic based on transaction properties
        if transaction.type == TransactionType.INCOME:
            suggestions.append({
                "category": TaxCategory.NON_DEDUCTIBLE,
                "confidence": 0.9,
                "reason": "Income is typically taxable",
                "suggested_notes": "Regular income"
            })

        return suggestions
