"""Report generation service for the Financial Planner application."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sqlalchemy.orm import Session
from ..models.models import User, Transaction, Budget, Debt, Investment
from . import budget_service, transaction_service, debt_service, investment_service

class ReportService:
    """Service for generating financial reports and visualizations."""

    def __init__(self):
        """Initialize the report service with required services."""
        self.budget_svc = budget_service.BudgetService()
        self.transaction_svc = transaction_service.TransactionService()
        self.debt_svc = debt_service.DebtService()
        self.investment_svc = investment_service.InvestmentService()
        
        # Set up plotting style
        plt.style.use('default')  # Use default style first
        sns.set_theme()  # Apply seaborn theme on top

    def generate_monthly_report(
        self,
        db: Session,
        user_id: int,
        month: datetime
    ) -> Dict[str, any]:
        """Generate a comprehensive monthly financial report."""
        # Get all relevant data
        budget_summary = self.budget_svc.get_budget_summary(db, user_id, month)
        transactions = self.transaction_svc.get_transactions(
            db, user_id,
            start_date=month.replace(day=1),
            end_date=(month.replace(day=1) + timedelta(days=32)).replace(day=1)
        )
        debt_summary = self.debt_svc.get_debt_summary(db, user_id)
        investment_summary = self.investment_svc.get_portfolio_value(db, user_id)
        
        return {
            "month": month.strftime("%B %Y"),
            "budget_summary": budget_summary,
            "transaction_summary": self._summarize_transactions(transactions),
            "debt_summary": debt_summary,
            "investment_summary": investment_summary,
            "charts": self._generate_monthly_charts(
                budget_summary,
                transactions,
                debt_summary,
                investment_summary
            )
        }

    def _summarize_transactions(
        self,
        transactions: List[Transaction]
    ) -> Dict[str, any]:
        """Summarize transactions by category and type."""
        df = pd.DataFrame([
            {
                "amount": t.amount,
                "category": t.category,
                "type": t.type.value,
                "date": t.date
            }
            for t in transactions
        ])
        
        if df.empty:
            return {
                "total_income": 0,
                "total_expenses": 0,
                "net_cash_flow": 0,
                "categories": []
            }
            
        summary = {
            "total_income": float(df[df["type"] == "income"]["amount"].sum()),
            "total_expenses": float(df[df["type"] == "expense"]["amount"].sum()),
            "categories": []
        }
        
        for category in df["category"].unique():
            cat_data = df[df["category"] == category]
            summary["categories"].append({
                "category": category,
                "total": float(cat_data["amount"].sum()),
                "count": len(cat_data),
                "average": float(cat_data["amount"].mean())
            })
            
        summary["net_cash_flow"] = summary["total_income"] - summary["total_expenses"]
        return summary

    def _generate_monthly_charts(
        self,
        budget_summary: Dict,
        transactions: List[Transaction],
        debt_summary: Dict,
        investment_summary: Dict
    ) -> Dict[str, str]:
        """Generate charts for monthly report."""
        charts = {}
        
        # Budget vs Actual Spending
        plt.figure(figsize=(10, 6))
        categories = [cat["category"] for cat in budget_summary["categories"]]
        budgeted = [cat["budgeted"] for cat in budget_summary["categories"]]
        spent = [cat["spent"] for cat in budget_summary["categories"]]
        
        x = range(len(categories))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], budgeted, width, label='Budgeted')
        plt.bar([i + width/2 for i in x], spent, width, label='Actual')
        plt.xlabel('Categories')
        plt.ylabel('Amount')
        plt.title('Budget vs Actual Spending')
        plt.xticks(x, categories, rotation=45)
        plt.legend()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        charts["budget_comparison"] = base64.b64encode(buffer.getvalue()).decode()
        
        # Income vs Expenses Timeline
        df = pd.DataFrame([
            {
                "date": t.date,
                "amount": t.amount if t.type.value == "income" else -t.amount,
                "type": t.type.value
            }
            for t in transactions
        ])
        
        if not df.empty:
            plt.figure(figsize=(10, 6))
            df_grouped = df.groupby(['date', 'type'])['amount'].sum().unstack()
            df_grouped.plot(kind='line', marker='o')
            plt.title('Income vs Expenses Timeline')
            plt.xlabel('Date')
            plt.ylabel('Amount')
            plt.legend()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            plt.close()
            charts["income_expenses_timeline"] = base64.b64encode(buffer.getvalue()).decode()
        
        return charts

    def export_to_pdf(
        self,
        report_data: Dict[str, any],
        output_path: str
    ) -> str:
        """Export report data to PDF format."""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(f"Financial Report - {report_data['month']}", title_style))
        elements.append(Spacer(1, 20))
        
        # Budget Summary
        elements.append(Paragraph("Budget Summary", styles["Heading2"]))
        budget_data = [["Category", "Budgeted", "Spent", "Remaining"]]
        for cat in report_data["budget_summary"]["categories"]:
            budget_data.append([
                cat["category"],
                f"${cat['budgeted']:,.2f}",
                f"${cat['spent']:,.2f}",
                f"${cat['remaining']:,.2f}"
            ])
            
        budget_table = Table(budget_data)
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(budget_table)
        elements.append(Spacer(1, 20))
        
        # Add charts if available
        if "charts" in report_data:
            for chart_name, chart_data in report_data["charts"].items():
                img_data = base64.b64decode(chart_data)
                img_buffer = BytesIO(img_data)
                elements.append(Paragraph(f"{chart_name.replace('_', ' ').title()}", styles["Heading2"]))
                elements.append(Image(img_buffer))
                elements.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(elements)
        return output_path

    def calculate_financial_health_score(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, any]:
        """Calculate overall financial health score and provide insights."""
        # Get all necessary data
        budget_summary = self.budget_svc.get_budget_summary(db, user_id)
        debt_summary = self.debt_svc.get_debt_summary(db, user_id)
        investment_summary = self.investment_svc.get_portfolio_value(db, user_id)
        
        # Calculate component scores (0-100)
        scores = {
            "budget_management": self._calculate_budget_score(budget_summary),
            "debt_management": self._calculate_debt_score(debt_summary),
            "investment_health": self._calculate_investment_score(investment_summary),
            "savings_rate": self._calculate_savings_score(budget_summary)
        }
        
        # Calculate overall score (weighted average)
        weights = {
            "budget_management": 0.3,
            "debt_management": 0.3,
            "investment_health": 0.2,
            "savings_rate": 0.2
        }
        
        overall_score = sum(
            scores[component] * weights[component]
            for component in scores
        )
        
        return {
            "overall_score": overall_score,
            "component_scores": scores,
            "insights": self._generate_financial_insights(scores, budget_summary, debt_summary)
        }

    def _calculate_budget_score(self, budget_summary: Dict) -> float:
        """Calculate budget management score."""
        if budget_summary["total_budgeted"] == 0:
            return 0
            
        # Factors: Overspending ratio, budget utilization
        overspending_ratio = max(0, min(100, (
            1 - max(0, budget_summary["total_spent"] - budget_summary["total_budgeted"])
            / budget_summary["total_budgeted"]
        ) * 100))
        
        utilization_ratio = max(0, min(100, (
            budget_summary["total_spent"] / budget_summary["total_budgeted"]
            * 100
        )))
        
        return (overspending_ratio * 0.6 + utilization_ratio * 0.4)

    def _calculate_debt_score(self, debt_summary: Dict) -> float:
        """Calculate debt management score."""
        if debt_summary["total_original"] == 0:
            return 100
            
        # Factors: Debt reduction progress, debt-to-income ratio
        progress_score = debt_summary["progress_percentage"]
        return progress_score

    def _calculate_investment_score(self, investment_summary: Dict) -> float:
        """Calculate investment health score."""
        if investment_summary["total_cost"] == 0:
            return 0
            
        # Factors: Portfolio diversification, return on investment
        roi_percentage = (
            (investment_summary["total_value"] - investment_summary["total_cost"])
            / investment_summary["total_cost"] * 100
        )
        
        diversification_score = min(100, len(investment_summary["investments"]) * 10)
        
        return (max(0, roi_percentage) * 0.7 + diversification_score * 0.3)

    def _calculate_savings_score(self, budget_summary: Dict) -> float:
        """Calculate savings rate score."""
        if budget_summary["total_budgeted"] == 0:
            return 0
            
        # Calculate savings rate from budget categories
        savings_categories = [
            cat for cat in budget_summary["categories"]
            if "savings" in cat["category"].lower()
            or "investment" in cat["category"].lower()
        ]
        
        savings_rate = sum(cat["budgeted"] for cat in savings_categories) / budget_summary["total_budgeted"] * 100
        return min(100, savings_rate * 2)  # Score of 100 for 50% savings rate

    def _generate_financial_insights(
        self,
        scores: Dict[str, float],
        budget_summary: Dict,
        debt_summary: Dict
    ) -> List[str]:
        """Generate actionable insights based on financial health scores."""
        insights = []
        
        # Budget insights
        if scores["budget_management"] < 70:
            overspent_categories = [
                cat["category"] for cat in budget_summary["categories"]
                if cat["spent"] > cat["budgeted"]
            ]
            if overspent_categories:
                insights.append(
                    f"Consider reducing spending in these categories: {', '.join(overspent_categories)}"
                )
        
        # Debt insights
        if scores["debt_management"] < 70:
            insights.append(
                "Consider using the debt avalanche method to pay off high-interest debt first"
            )
        
        # Investment insights
        if scores["investment_health"] < 50:
            insights.append(
                "Consider diversifying your investment portfolio across different asset classes"
            )
        
        # Savings insights
        if scores["savings_rate"] < 60:
            insights.append(
                "Aim to save at least 20% of your income for long-term financial security"
            )
        
        return insights
