"""Command-line interface for the Financial Planner application."""
import click
from datetime import datetime
import os
from typing import Optional
from .app import FinancialPlanner
from .models.models import TransactionType

class CLI:
    """CLI wrapper for the Financial Planner application."""
    
    def __init__(self):
        """Initialize the CLI interface."""
        self.app = FinancialPlanner()
        self.current_month = datetime.now().replace(day=1)

    def start(self):
        """Start the CLI interface."""
        click.clear()
        click.echo("Welcome to Financial Planner!")
        
        while True:
            if not self.app.current_user:
                self._show_auth_menu()
            else:
                self._show_main_menu()

    def _show_auth_menu(self):
        """Show authentication menu."""
        click.echo("\nAuthentication Menu:")
        click.echo("1. Login")
        click.echo("2. Register")
        click.echo("3. Exit")
        
        choice = click.prompt("Select an option", type=int)
        
        if choice == 1:
            self._handle_login()
        elif choice == 2:
            self._handle_registration()
        elif choice == 3:
            click.echo("Goodbye!")
            exit(0)
        else:
            click.echo("Invalid option!")

    def _handle_login(self):
        """Handle user login."""
        username = click.prompt("Username")
        password = click.prompt("Password", hide_input=True)
        
        if self.app.login(username, password):
            click.echo("Login successful!")
        else:
            click.echo("Login failed!")

    def _handle_registration(self):
        """Handle user registration."""
        username = click.prompt("Username")
        email = click.prompt("Email")
        password = click.prompt("Password", hide_input=True)
        confirm_password = click.prompt("Confirm Password", hide_input=True)
        
        if password != confirm_password:
            click.echo("Passwords don't match!")
            return
            
        if self.app.register(username, email, password):
            click.echo("Registration successful!")
        else:
            click.echo("Registration failed!")

    def _show_main_menu(self):
        """Show main application menu."""
        click.clear()
        click.echo(f"\nWelcome, {self.app.current_user.username}!")
        click.echo(f"Current Month: {self.current_month.strftime('%B %Y')}")
        
        click.echo("\nMain Menu:")
        click.echo("1. Budget Management")
        click.echo("2. Transactions")
        click.echo("3. Investments")
        click.echo("4. Debt Management")
        click.echo("5. Reports")
        click.echo("6. Financial Health")
        click.echo("7. Change Month")
        click.echo("8. Logout")
        
        choice = click.prompt("Select an option", type=int)
        
        if choice == 1:
            self._show_budget_menu()
        elif choice == 2:
            self._show_transaction_menu()
        elif choice == 3:
            self._show_investment_menu()
        elif choice == 4:
            self._show_debt_menu()
        elif choice == 5:
            self._show_report_menu()
        elif choice == 6:
            self._show_financial_health()
        elif choice == 7:
            self._change_month()
        elif choice == 8:
            self.app.logout()
        else:
            click.echo("Invalid option!")

    def _show_budget_menu(self):
        """Show budget management menu."""
        while True:
            click.clear()
            click.echo("\nBudget Management:")
            click.echo("1. View Budget Summary")
            click.echo("2. Create Budget Category")
            click.echo("3. Back to Main Menu")
            
            choice = click.prompt("Select an option", type=int)
            
            if choice == 1:
                summary = self.app.get_budget_summary(self.current_month)
                self._display_budget_summary(summary)
                click.pause()
            elif choice == 2:
                category = click.prompt("Category name")
                amount = click.prompt("Budget amount", type=float)
                self.app.create_budget(category, amount, self.current_month)
                click.echo("Budget category created!")
                click.pause()
            elif choice == 3:
                break
            else:
                click.echo("Invalid option!")

    def _show_transaction_menu(self):
        """Show transaction management menu."""
        while True:
            click.clear()
            click.echo("\nTransactions:")
            click.echo("1. Add Income")
            click.echo("2. Add Expense")
            click.echo("3. View Recent Transactions")
            click.echo("4. Back to Main Menu")
            
            choice = click.prompt("Select an option", type=int)
            
            if choice == 1:
                self._add_transaction(TransactionType.INCOME)
            elif choice == 2:
                self._add_transaction(TransactionType.EXPENSE)
            elif choice == 3:
                # TODO: Implement transaction viewing
                click.echo("Feature coming soon!")
                click.pause()
            elif choice == 4:
                break
            else:
                click.echo("Invalid option!")

    def _show_investment_menu(self):
        """Show investment management menu."""
        while True:
            click.clear()
            click.echo("\nInvestments:")
            click.echo("1. View Portfolio")
            click.echo("2. Add Investment")
            click.echo("3. Back to Main Menu")
            
            choice = click.prompt("Select an option", type=int)
            
            if choice == 1:
                summary = self.app.get_portfolio_summary()
                self._display_portfolio_summary(summary)
                click.pause()
            elif choice == 2:
                self._add_investment()
            elif choice == 3:
                break
            else:
                click.echo("Invalid option!")

    def _show_debt_menu(self):
        """Show debt management menu."""
        while True:
            click.clear()
            click.echo("\nDebt Management:")
            click.echo("1. View Debt Summary")
            click.echo("2. Add Debt")
            click.echo("3. Get Payment Strategy")
            click.echo("4. Back to Main Menu")
            
            choice = click.prompt("Select an option", type=int)
            
            if choice == 1:
                # TODO: Implement debt summary view
                click.echo("Feature coming soon!")
                click.pause()
            elif choice == 2:
                self._add_debt()
            elif choice == 3:
                self._show_payment_strategy()
            elif choice == 4:
                break
            else:
                click.echo("Invalid option!")

    def _show_report_menu(self):
        """Show report generation menu."""
        while True:
            click.clear()
            click.echo("\nReports:")
            click.echo("1. Generate Monthly Report")
            click.echo("2. Back to Main Menu")
            
            choice = click.prompt("Select an option", type=int)
            
            if choice == 1:
                report_path = self.app.generate_monthly_report(self.current_month)
                click.echo(f"Report generated: {report_path}")
                click.pause()
            elif choice == 2:
                break
            else:
                click.echo("Invalid option!")

    def _show_financial_health(self):
        """Show financial health score and insights."""
        health_data = self.app.get_financial_health()
        
        click.clear()
        click.echo("\nFinancial Health Report")
        click.echo("=" * 50)
        click.echo(f"Overall Score: {health_data['overall_score']:.2f}/100")
        click.echo("\nComponent Scores:")
        for component, score in health_data["component_scores"].items():
            click.echo(f"- {component.replace('_', ' ').title()}: {score:.2f}/100")
        
        click.echo("\nInsights:")
        for insight in health_data["insights"]:
            click.echo(f"- {insight}")
        
        click.pause()

    def _change_month(self):
        """Change the current working month."""
        while True:
            click.clear()
            click.echo("\nChange Month:")
            click.echo("1. Previous Month")
            click.echo("2. Next Month")
            click.echo("3. Back to Main Menu")
            
            choice = click.prompt("Select an option", type=int)
            
            if choice == 1:
                self.current_month = (self.current_month.replace(day=1) - timedelta(days=1)).replace(day=1)
            elif choice == 2:
                self.current_month = (self.current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
            elif choice == 3:
                break
            else:
                click.echo("Invalid option!")

    def _add_transaction(self, transaction_type: TransactionType):
        """Add a new transaction."""
        amount = click.prompt("Amount", type=float)
        category = click.prompt("Category")
        description = click.prompt("Description (optional)", default="")
        
        self.app.add_transaction(
            amount=amount,
            category=category,
            transaction_type=transaction_type,
            description=description or None
        )
        click.echo("Transaction added successfully!")
        click.pause()

    def _add_investment(self):
        """Add a new investment."""
        investment_type = click.prompt("Type (stock/crypto)")
        symbol = click.prompt("Symbol").upper()
        quantity = click.prompt("Quantity", type=float)
        purchase_price = click.prompt("Purchase Price", type=float)
        
        self.app.add_investment(
            investment_type=investment_type,
            symbol=symbol,
            quantity=quantity,
            purchase_price=purchase_price
        )
        click.echo("Investment added successfully!")
        click.pause()

    def _add_debt(self):
        """Add a new debt."""
        name = click.prompt("Debt name")
        total_amount = click.prompt("Total amount", type=float)
        interest_rate = click.prompt("Interest rate (%)", type=float)
        minimum_payment = click.prompt("Minimum monthly payment", type=float)
        
        self.app.add_debt(
            name=name,
            total_amount=total_amount,
            interest_rate=interest_rate / 100,  # Convert percentage to decimal
            minimum_payment=minimum_payment
        )
        click.echo("Debt added successfully!")
        click.pause()

    def _show_payment_strategy(self):
        """Show debt payment strategy."""
        monthly_budget = click.prompt("Monthly budget for debt payments", type=float)
        strategy = click.prompt(
            "Strategy (avalanche/snowball)",
            type=click.Choice(['avalanche', 'snowball']),
            default='avalanche'
        )
        
        payment_plan = self.app.get_debt_payment_strategy(monthly_budget, strategy)
        
        click.clear()
        click.echo(f"\nDebt Payment Strategy ({strategy.title()} Method)")
        click.echo("=" * 50)
        
        for payment in payment_plan:
            click.echo(f"\nDebt: {payment['name']}")
            click.echo(f"Minimum Payment: ${payment['minimum_payment']:,.2f}")
            click.echo(f"Suggested Payment: ${payment['suggested_payment']:,.2f}")
            click.echo(f"Remaining Amount: ${payment['remaining_amount']:,.2f}")
            click.echo(f"Interest Rate: {payment['interest_rate']:.2f}%")
        
        click.pause()

    def _display_budget_summary(self, summary: dict):
        """Display budget summary."""
        click.clear()
        click.echo("\nBudget Summary")
        click.echo("=" * 50)
        click.echo(f"Total Budgeted: ${summary['total_budgeted']:,.2f}")
        click.echo(f"Total Spent: ${summary['total_spent']:,.2f}")
        click.echo(f"Total Remaining: ${summary['total_remaining']:,.2f}")
        
        click.echo("\nCategory Breakdown:")
        for category in summary["categories"]:
            click.echo(f"\n{category['category']}")
            click.echo(f"Budgeted: ${category['budgeted']:,.2f}")
            click.echo(f"Spent: ${category['spent']:,.2f}")
            click.echo(f"Remaining: ${category['remaining']:,.2f}")
            click.echo(f"Usage: {category['usage_percentage']:.1f}%")

    def _display_portfolio_summary(self, summary: dict):
        """Display investment portfolio summary."""
        click.clear()
        click.echo("\nInvestment Portfolio Summary")
        click.echo("=" * 50)
        click.echo(f"Total Value: ${summary['total_value']:,.2f}")
        click.echo(f"Total Cost: ${summary['total_cost']:,.2f}")
        click.echo(f"Total Gain/Loss: ${summary['total_gain_loss']:,.2f}")
        click.echo(f"Return: {summary['total_gain_loss_percentage']:.2f}%")
        
        click.echo("\nInvestments:")
        for inv in summary["investments"]:
            click.echo(f"\n{inv['symbol']} ({inv['type']})")
            click.echo(f"Quantity: {inv['quantity']}")
            click.echo(f"Purchase Price: ${inv['purchase_price']:,.2f}")
            click.echo(f"Current Price: ${inv['current_price']:,.2f}")
            click.echo(f"Current Value: ${inv['current_value']:,.2f}")
            click.echo(f"Gain/Loss: ${inv['gain_loss']:,.2f} ({inv['gain_loss_percentage']:.2f}%)")

def main():
    """Main entry point for the CLI application."""
    cli = CLI()
    cli.start()

if __name__ == "__main__":
    main()
