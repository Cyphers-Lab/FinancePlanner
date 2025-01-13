"""Dashboard page for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QScrollArea, QGridLayout)
from ..dialogs.settings_dialog import SettingsDialog
from PyQt5.QtCore import Qt
from datetime import datetime

class DashboardPage(QWidget):
    """Dashboard page showing overview of financial status and navigation."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header with navigation
        header = QHBoxLayout()
        title = QLabel('Dashboard')
        title.setStyleSheet('font-size: 24px; font-weight: bold;')
        header.addWidget(title)
        
        # Navigation buttons
        nav_buttons = QHBoxLayout()
        nav_buttons.setAlignment(Qt.AlignRight)
        
        buttons = [
            ('Budget', self.main_window.show_budget_page),
            ('Transactions', self.main_window.show_transaction_page),
            ('Investments', self.main_window.show_investment_page),
            ('Net Worth', self.main_window.show_net_worth_page),
            ('Savings', self.main_window.show_savings_page),
            ('Debt', self.main_window.show_debt_page),
            ('Tax Planning', self.main_window.show_tax_page),
            ('Forecast', self.main_window.show_forecast_page),
            ('Reports', self.main_window.show_report_page),
            ('Settings', self.show_settings),
            ('Logout', self.main_window.handle_logout)
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            nav_buttons.addWidget(btn)
            
        header.addLayout(nav_buttons)
        layout.addLayout(header)
        
        # Create scroll area for dashboard content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        content_layout = QGridLayout(content)
        
        # Financial Health Score
        health_widget = self.create_widget('Financial Health')
        self.health_score = QLabel('Loading...')
        self.health_score.setStyleSheet('font-size: 36px; font-weight: bold; color: #4CAF50;')
        self.health_score.setAlignment(Qt.AlignCenter)
        health_widget.layout().addWidget(self.health_score)
        content_layout.addWidget(health_widget, 0, 0)
        
        # Budget Summary
        budget_widget = self.create_widget('Budget Summary')
        self.budget_summary = QLabel('Loading...')
        budget_widget.layout().addWidget(self.budget_summary)
        content_layout.addWidget(budget_widget, 0, 1)
        
        # Recent Transactions
        transactions_widget = self.create_widget('Recent Transactions')
        self.transactions_list = QLabel('Loading...')
        transactions_widget.layout().addWidget(self.transactions_list)
        content_layout.addWidget(transactions_widget, 1, 0)
        
        # Portfolio Summary
        portfolio_widget = self.create_widget('Investment Portfolio')
        self.portfolio_summary = QLabel('Loading...')
        portfolio_widget.layout().addWidget(self.portfolio_summary)
        content_layout.addWidget(portfolio_widget, 1, 1)
        
        # Tax Summary
        tax_widget = self.create_widget('Tax Summary')
        self.tax_summary = QLabel('Loading...')
        tax_widget.layout().addWidget(self.tax_summary)
        content_layout.addWidget(tax_widget, 2, 0)
        
        # Smart Insights
        insights_widget = self.create_widget('Smart Insights')
        insights_layout = QVBoxLayout()
        
        # Insights list
        self.insights_list = QWidget()
        self.insights_list_layout = QVBoxLayout(self.insights_list)
        self.insights_list_layout.setSpacing(10)
        self.insights_list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for insights
        insights_scroll = QScrollArea()
        insights_scroll.setWidgetResizable(True)
        insights_scroll.setWidget(self.insights_list)
        insights_scroll.setFrameShape(QFrame.NoFrame)
        insights_scroll.setMinimumHeight(400)
        
        insights_layout.addWidget(insights_scroll)
        
        # Generate insights button
        generate_btn = QPushButton('Generate New Insights')
        generate_btn.clicked.connect(self.generate_insights)
        insights_layout.addWidget(generate_btn)
        
        insights_widget.layout().addLayout(insights_layout)
        content_layout.addWidget(insights_widget, 2, 1, 2, 1)  # Move to right column, span 2 rows
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Style the page
        self.style_widgets()
        
    def create_widget(self, title):
        """Create a styled widget with title."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setStyleSheet('font-size: 18px; font-weight: bold; margin-bottom: 10px;')
        layout.addWidget(title_label)
        
        return widget
        
    def style_widgets(self):
        """Apply styles to widgets."""
        button_style = """
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:last-child {
                background-color: #f44336;
            }
            QPushButton:last-child:hover {
                background-color: #da190b;
            }
        """
        
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)
            
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.main_window)
        dialog.exec_()
        
    def create_insight_widget(self, insight):
        """Create a widget to display a single insight."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
            }
            QLabel {
                margin-bottom: 5px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        # Priority indicator and title
        header = QHBoxLayout()
        priority_color = {
            'urgent': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }.get(insight['priority'], '#6c757d')
        
        priority_indicator = QLabel('●')
        priority_indicator.setStyleSheet(f'color: {priority_color}; font-size: 16px;')
        header.addWidget(priority_indicator)
        
        title = QLabel(insight['title'])
        title.setStyleSheet('font-weight: bold; font-size: 14px;')
        header.addWidget(title)
        header.addStretch()
        
        # Action buttons
        if not insight['is_acted_upon']:
            act_btn = QPushButton('Act')
            act_btn.setFixedWidth(60)
            act_btn.clicked.connect(lambda: self.mark_insight_acted_upon(insight['id']))
            header.addWidget(act_btn)
        
        layout.addLayout(header)
        
        # Description and recommendation
        description = QLabel(insight['description'])
        description.setWordWrap(True)
        layout.addWidget(description)
        
        recommendation = QLabel(f"<b>Recommendation:</b> {insight['recommendation']}")
        recommendation.setWordWrap(True)
        layout.addWidget(recommendation)
        
        # Feedback section if not rated
        if insight['feedback_rating'] is None:
            feedback = QHBoxLayout()
            feedback.addWidget(QLabel('Was this helpful?'))
            
            for rating in range(1, 6):
                rate_btn = QPushButton(str(rating))
                rate_btn.setFixedWidth(30)
                rate_btn.clicked.connect(
                    lambda r=rating, i=insight['id']: self.rate_insight(i, r)
                )
                feedback.addWidget(rate_btn)
            
            feedback.addStretch()
            layout.addLayout(feedback)
        
        return widget

    def generate_insights(self):
        """Generate new insights."""
        try:
            insights = self.main_window.app.generate_insights()
            self.refresh_insights()
        except Exception as e:
            self.main_window.show_error(f'Error generating insights: {str(e)}')

    def mark_insight_acted_upon(self, insight_id: int):
        """Mark an insight as acted upon."""
        try:
            self.main_window.app.mark_insight_acted_upon(insight_id)
            self.refresh_insights()
        except Exception as e:
            self.main_window.show_error(f'Error updating insight: {str(e)}')

    def rate_insight(self, insight_id: int, rating: int):
        """Rate an insight."""
        try:
            self.main_window.app.rate_insight(insight_id, rating)
            self.refresh_insights()
        except Exception as e:
            self.main_window.show_error(f'Error rating insight: {str(e)}')

    def refresh_insights(self):
        """Refresh the insights list."""
        try:
            # Clear existing insights
            while self.insights_list_layout.count():
                item = self.insights_list_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Get and display new insights
            insights = self.main_window.app.get_insights()
            for insight in insights:
                self.insights_list_layout.addWidget(self.create_insight_widget(insight))
            
            # Add stretch to push insights to the top
            self.insights_list_layout.addStretch()
            
        except Exception as e:
            self.main_window.show_error(f'Error refreshing insights: {str(e)}')

    def refresh_data(self):
        """Refresh dashboard data."""
        try:
            self.refresh_insights()
            # Get financial health score
            health_data = self.main_window.app.get_financial_health()
            self.health_score.setText(f"{health_data['overall_score']:.0f}%")
            
            # Get budget summary
            budget_data = self.main_window.app.get_budget_summary(datetime.now())
            budget_text = f"""
                <p><b>Total Budget:</b> {self.main_window.app.format_amount(budget_data['total_budgeted'])}</p>
                <p><b>Spent:</b> {self.main_window.app.format_amount(budget_data['total_spent'])}</p>
                <p><b>Remaining:</b> {self.main_window.app.format_amount(budget_data['total_remaining'])}</p>
            """
            self.budget_summary.setText(budget_text)
            
            # Get portfolio summary
            portfolio_data = self.main_window.app.get_portfolio_summary()
            portfolio_text = f"""
                <p><b>Total Value:</b> {self.main_window.app.format_amount(portfolio_data['total_value'])}</p>
                <p><b>Total Gain/Loss:</b> {self.main_window.app.format_amount(portfolio_data['total_gain_loss'])}</p>
                <p><b>Return:</b> {portfolio_data['total_gain_loss_percentage']:.1f}%</p>
            """
            self.portfolio_summary.setText(portfolio_text)
            
            # Get tax summary
            try:
                tax_service = self.main_window.app.get_service('tax_service')
                tax_summary = tax_service.get_tax_summary(
                    self.main_window.app.current_user.id,
                    datetime.now().year
                )
                tax_text = f"""
                    <p><b>Total Income:</b> {self.main_window.app.format_amount(tax_summary['total_income'])}</p>
                    <p><b>Total Deductions:</b> {self.main_window.app.format_amount(tax_summary['total_deductible_expenses'])}</p>
                    <p><b>Uncategorized Transactions:</b> {len(tax_summary['uncategorized_transactions'])}</p>
                """
                self.tax_summary.setText(tax_text)
            except Exception:
                self.tax_summary.setText("Set up your tax profile to view summary")
            
            # Get recent transactions
            transactions = self.main_window.app.get_transactions(
                start_date=datetime.now().replace(day=1),  # Get this month's transactions
                end_date=datetime.now()
            )[:5]  # Get last 5 transactions since they're ordered by date desc
            
            if transactions:
                transaction_texts = []
                for t in transactions:
                    transaction_texts.append(
                        f"<p>{t['date'].strftime('%Y-%m-%d')} - {t['description']}: {self.main_window.app.format_amount(t['amount'])}</p>"
                    )
                self.transactions_list.setText('\n'.join(transaction_texts))
            else:
                self.transactions_list.setText('No recent transactions')
            
        except Exception as e:
            self.main_window.show_error(f'Error refreshing dashboard: {str(e)}')
