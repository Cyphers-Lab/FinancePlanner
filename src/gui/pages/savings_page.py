"""Savings goals page for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QGridLayout, QLineEdit,
                           QComboBox, QDateEdit, QProgressBar, QScrollArea,
                           QSpinBox, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

class SavingsPage(QWidget):
    """Savings page for managing savings goals."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel('Savings Goals')
        title.setStyleSheet('font-size: 24px; font-weight: bold;')
        header.addWidget(title)
        
        # Add Goal button
        add_btn = QPushButton('Add New Goal')
        add_btn.clicked.connect(self.show_add_goal_form)
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        header.addStretch()
        header.addWidget(add_btn)
        
        # Back button
        back_btn = QPushButton('Back to Dashboard')
        back_btn.clicked.connect(self.main_window.show_dashboard)
        back_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        header.addWidget(back_btn)
        layout.addLayout(header)
        
        # Summary charts
        charts_frame = QFrame()
        charts_frame.setFrameStyle(QFrame.StyledPanel)
        charts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        charts_layout = QHBoxLayout(charts_frame)
        
        # Progress Overview Chart
        self.progress_figure = plt.figure(figsize=(6, 4))
        self.progress_canvas = FigureCanvas(self.progress_figure)
        charts_layout.addWidget(self.progress_canvas)
        
        # Timeline Chart
        self.timeline_figure = plt.figure(figsize=(6, 4))
        self.timeline_canvas = FigureCanvas(self.timeline_figure)
        charts_layout.addWidget(self.timeline_canvas)
        
        layout.addWidget(charts_frame)
        
        # Create scroll area for goals
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        self.goals_layout = QVBoxLayout(content)
        
        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(['All', 'Critical', 'High', 'Medium', 'Low'])
        self.priority_filter.currentTextChanged.connect(self.refresh_goals)
        filter_layout.addWidget(self.priority_filter)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(['All', 'One-time', 'Recurring'])
        self.type_filter.currentTextChanged.connect(self.refresh_goals)
        filter_layout.addWidget(self.type_filter)
        
        self.show_completed = QCheckBox("Show completed goals")
        self.show_completed.stateChanged.connect(self.refresh_goals)
        filter_layout.addWidget(self.show_completed)
        
        filter_layout.addStretch()
        self.goals_layout.addLayout(filter_layout)
        
        # Goal creation form (initially hidden)
        self.goal_form = self.create_goal_form()
        self.goal_form.hide()
        self.goals_layout.addWidget(self.goal_form)
        
        # Goals grid
        self.goals_grid = QGridLayout()
        self.goals_layout.addLayout(self.goals_grid)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Refresh goals list
        self.refresh_goals()
        
    def create_goal_form(self) -> QFrame:
        """Create the goal creation/editing form."""
        form = QFrame()
        form.setFrameStyle(QFrame.StyledPanel)
        form.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        
        form_layout = QGridLayout(form)
        
        # Name input
        form_layout.addWidget(QLabel('Goal Name:'), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('e.g., Emergency Fund, Vacation')
        form_layout.addWidget(self.name_input, 0, 1)
        
        # Target amount input
        form_layout.addWidget(QLabel('Target Amount:'), 1, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('Enter target amount')
        form_layout.addWidget(self.amount_input, 1, 1)
        
        # Description input
        form_layout.addWidget(QLabel('Description:'), 2, 0)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText('Enter description')
        form_layout.addWidget(self.description_input, 2, 1)
        
        # Target date input
        form_layout.addWidget(QLabel('Target Date:'), 3, 0)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate().addMonths(1))
        self.date_input.setCalendarPopup(True)
        form_layout.addWidget(self.date_input, 3, 1)
        
        # Priority selection
        form_layout.addWidget(QLabel('Priority:'), 4, 0)
        self.priority_select = QComboBox()
        self.priority_select.addItems(['low', 'medium', 'high', 'critical'])
        self.priority_select.setCurrentText('medium')
        form_layout.addWidget(self.priority_select, 4, 1)
        
        # Goal type selection
        form_layout.addWidget(QLabel('Goal Type:'), 5, 0)
        self.type_select = QComboBox()
        self.type_select.addItems(['one_time', 'recurring', 'emergency_fund'])
        self.type_select.currentTextChanged.connect(self.on_goal_type_changed)
        form_layout.addWidget(self.type_select, 5, 1)

        # Emergency fund specific fields (initially hidden)
        self.emergency_fund_frame = QFrame()
        emergency_layout = QGridLayout(self.emergency_fund_frame)
        
        emergency_layout.addWidget(QLabel('Monthly Expenses:'), 0, 0)
        self.monthly_expenses_input = QLineEdit()
        self.monthly_expenses_input.setPlaceholderText('Enter monthly expenses')
        emergency_layout.addWidget(self.monthly_expenses_input, 0, 1)
        
        emergency_layout.addWidget(QLabel('Months Coverage:'), 1, 0)
        self.months_coverage_input = QSpinBox()
        self.months_coverage_input.setRange(3, 12)
        self.months_coverage_input.setValue(6)
        self.months_coverage_input.valueChanged.connect(self.update_target_amount)
        emergency_layout.addWidget(self.months_coverage_input, 1, 1)
        
        emergency_layout.addWidget(QLabel('Critical Threshold (%):'), 2, 0)
        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(10, 90)
        self.threshold_input.setValue(50)
        emergency_layout.addWidget(self.threshold_input, 2, 1)
        
        form_layout.addWidget(self.emergency_fund_frame, 6, 0, 1, 2)
        self.emergency_fund_frame.hide()
        
        # Allocation rules
        form_layout.addWidget(QLabel('Allocation Rule:'), 7, 0)
        rule_layout = QHBoxLayout()
        
        self.rule_type = QComboBox()
        self.rule_type.addItems(['percentage', 'fixed_amount'])
        rule_layout.addWidget(self.rule_type)
        
        self.rule_value = QSpinBox()
        self.rule_value.setRange(1, 100)
        self.rule_value.setValue(10)
        rule_layout.addWidget(self.rule_value)
        
        form_layout.addLayout(rule_layout, 6, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Save Goal')
        save_btn.clicked.connect(self.save_goal)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(lambda: self.goal_form.hide())
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        form_layout.addLayout(button_layout, 8, 0, 1, 2)
        
        return form
        
    def update_charts(self, goals: list):
        """Update the summary charts."""
        # Clear previous charts
        self.progress_figure.clear()
        self.timeline_figure.clear()
        
        if not goals:
            # Show "No data" message in both charts
            ax1 = self.progress_figure.add_subplot(111)
            ax1.text(0.5, 0.5, 'No goals available\nPlease log in or create a goal',
                    ha='center', va='center', fontsize=12)
            ax1.axis('off')
            
            ax2 = self.timeline_figure.add_subplot(111)
            ax2.text(0.5, 0.5, 'No goals available\nPlease log in or create a goal',
                    ha='center', va='center', fontsize=12)
            ax2.axis('off')
            
            self.progress_canvas.draw()
            self.timeline_canvas.draw()
            return
            
        # Progress Overview (Pie Chart)
        ax1 = self.progress_figure.add_subplot(111)
        completed = sum(1 for g in goals if g['progress'] >= 100)
        in_progress = sum(1 for g in goals if 0 < g['progress'] < 100)
        not_started = sum(1 for g in goals if g['progress'] == 0)
        
        ax1.pie([completed, in_progress, not_started],
                labels=['Completed', 'In Progress', 'Not Started'],
                colors=['#4CAF50', '#2196F3', '#FFC107'],
                autopct='%1.1f%%')
        ax1.set_title('Goals Overview')
        
        # Timeline Chart
        ax2 = self.timeline_figure.add_subplot(111)
        
        # Filter goals with target dates
        dated_goals = [g for g in goals if g['target_date']]
        if dated_goals:
            goals_data = [(g['name'], g['target_date'], g['progress']) for g in dated_goals]
            names, dates, progress = zip(*goals_data)
            
            # Create timeline
            ax2.barh(range(len(dates)), 
                    [(d - datetime.now()).days for d in dates],
                    left=[0] * len(dates),
                    color=[plt.cm.RdYlGn(p/100) for p in progress])
            
            ax2.set_yticks(range(len(names)))
            ax2.set_yticklabels(names)
            ax2.set_xlabel('Days Remaining')
            ax2.set_title('Goals Timeline')
            
            # Add progress annotations
            for i, p in enumerate(progress):
                ax2.text(5, i, f'{p:.1f}%', va='center')
        
        self.progress_canvas.draw()
        self.timeline_canvas.draw()
        
    def on_goal_type_changed(self, goal_type: str):
        """Handle goal type selection changes."""
        if goal_type == 'emergency_fund':
            self.emergency_fund_frame.show()
            self.priority_select.setCurrentText('critical')
            self.priority_select.setEnabled(False)
            self.name_input.setText('Emergency Fund')
            self.name_input.setEnabled(False)
            self.date_input.setEnabled(False)
            if self.monthly_expenses_input.text():
                self.update_target_amount()
        else:
            self.emergency_fund_frame.hide()
            self.priority_select.setEnabled(True)
            self.name_input.setEnabled(True)
            self.name_input.clear()
            self.date_input.setEnabled(True)

    def update_target_amount(self):
        """Update target amount based on monthly expenses and coverage."""
        if self.type_select.currentText() == 'emergency_fund':
            try:
                monthly_expenses = float(self.monthly_expenses_input.text())
                months_coverage = self.months_coverage_input.value()
                target_amount = monthly_expenses * months_coverage
                self.amount_input.setText(str(target_amount))
            except ValueError:
                pass

    def create_goal_widget(self, goal: dict) -> QFrame:
        """Create a widget to display a savings goal."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        # Header with name and buttons
        header = QHBoxLayout()
        name = QLabel(goal['name'])
        name.setStyleSheet('font-size: 18px; font-weight: bold;')
        header.addWidget(name)
        
        if goal.get('is_paused'):
            status = QLabel('PAUSED')
            status.setStyleSheet('color: #f44336; font-weight: bold;')
            header.addWidget(status)
            
        edit_btn = QPushButton('Edit')
        edit_btn.clicked.connect(lambda: self.edit_goal(goal))
        delete_btn = QPushButton('Delete')
        delete_btn.clicked.connect(lambda: self.delete_goal(goal['id']))
        
        header.addStretch()
        header.addWidget(edit_btn)
        header.addWidget(delete_btn)
        layout.addLayout(header)
        
        # Progress bar with gradient based on progress
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress_val = int(goal['progress'])
        progress.setValue(progress_val)
        progress.setFormat(f"{self.main_window.app.format_amount(goal['current_amount'])} of {self.main_window.app.format_amount(goal['target_amount'])} ({goal['progress']:.1f}%)")
        
        # Color gradient based on progress
        if progress_val >= 100:
            color = "#4CAF50"  # Green for completed
        elif progress_val >= 75:
            color = "#8BC34A"  # Light green for near completion
        elif progress_val >= 50:
            color = "#FFC107"  # Yellow for halfway
        elif progress_val >= 25:
            color = "#FF9800"  # Orange for started
        else:
            color = "#f44336"  # Red for just started
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        layout.addWidget(progress)
        
        # Add withdrawal button for emergency funds
        if goal['goal_type'] == 'emergency_fund':
            withdraw_btn = QPushButton('Record Withdrawal')
            withdraw_btn.clicked.connect(lambda: self.show_withdrawal_dialog(goal))
            withdraw_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            header.addWidget(withdraw_btn)

        # Details with enhanced formatting
        priority_color = {
            'critical': '#f44336',
            'high': '#FF9800',
            'medium': '#2196F3',
            'low': '#4CAF50'
        }.get(goal['priority'], '#000000')
        
        days_remaining = (goal['target_date'] - datetime.now()).days if goal['target_date'] else None
        deadline_color = '#f44336' if days_remaining and days_remaining < 30 else '#000000'
        
        details = QLabel(f"""
            <p><b>Description:</b> {goal.get('description', 'N/A')}</p>
            {self.get_emergency_fund_details(goal) if goal['goal_type'] == 'emergency_fund' else ''}
            <p><b>Priority:</b> <span style='color: {priority_color};'>{goal['priority'].upper()}</span></p>
            <p><b>Type:</b> {goal['goal_type'].replace('_', ' ').title()}</p>
            <p><b>Target Date:</b> <span style='color: {deadline_color};'>
                {goal['target_date'].strftime('%Y-%m-%d') if goal['target_date'] else 'No deadline'}
                {f' ({days_remaining} days remaining)' if days_remaining else ''}
            </span></p>
        """)
        layout.addWidget(details)
        
        # Allocation rule with visual indicator
        if goal.get('allocation_rules'):
            rule = goal['allocation_rules']
            if 'percentage' in rule:
                rule_text = f"Allocating {rule['percentage']}% of income"
                indicator = "📊"
            else:
                rule_text = f"Allocating {self.main_window.app.format_amount(rule['fixed_amount'])} per income"
                indicator = "💰"
            allocation = QLabel(f"<p><b>Allocation Rule:</b> {indicator} {rule_text}</p>")
            layout.addWidget(allocation)
            
        # Social sharing button
        if goal['progress'] >= 100:
            share_btn = QPushButton('🎉 Share Achievement')
            share_btn.clicked.connect(lambda: self.share_achievement(goal))
            share_btn.setStyleSheet("""
                QPushButton {
                    background-color: #673AB7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #5E35B1;
                }
            """)
            layout.addWidget(share_btn)
        
        return widget
        
    def show_add_goal_form(self):
        """Show the goal creation form."""
        self.goal_form.show()
        self.name_input.clear()
        self.amount_input.clear()
        self.description_input.clear()
        self.date_input.setDate(QDate.currentDate().addMonths(1))
        self.priority_select.setCurrentText('medium')
        self.type_select.setCurrentText('one_time')
        self.rule_type.setCurrentText('percentage')
        self.rule_value.setValue(10)
        
    def get_emergency_fund_details(self, goal: dict) -> str:
        """Get HTML formatted emergency fund specific details."""
        if not goal.get('monthly_expenses'):
            return ''
            
        months_coverage = goal['current_amount'] / goal['monthly_expenses']
        target_months = goal['months_coverage']
        
        coverage_color = '#4CAF50' if months_coverage >= target_months else (
            '#FFC107' if months_coverage >= target_months * 0.75 else '#f44336'
        )
        
        last_withdrawal = goal.get('last_withdrawal')
        withdrawal_text = (f"Last withdrawal: {last_withdrawal.strftime('%Y-%m-%d')}"
                         if last_withdrawal else "No withdrawals recorded")
        
        return f"""
            <p><b>Monthly Expenses:</b> {self.main_window.app.format_amount(goal['monthly_expenses'])}</p>
            <p><b>Current Coverage:</b> <span style='color: {coverage_color};'>
                {months_coverage:.1f} months of {target_months} months target
            </span></p>
            <p><b>Critical Threshold:</b> {goal['critical_threshold'] * 100}% of target</p>
            <p><i>{withdrawal_text}</i></p>
        """

    def show_withdrawal_dialog(self, goal: dict):
        """Show dialog for recording emergency fund withdrawal."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Emergency Fund Withdrawal")
        layout = QVBoxLayout(dialog)
        
        # Amount input
        layout.addWidget(QLabel("Withdrawal Amount:"))
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("Enter amount to withdraw")
        layout.addWidget(amount_input)
        
        # Description input
        layout.addWidget(QLabel("Reason for Withdrawal:"))
        reason_input = QLineEdit()
        reason_input.setPlaceholderText("Enter reason for withdrawal")
        layout.addWidget(reason_input)
        
        # Warning label
        warning = QLabel(f"Available balance: {self.main_window.app.format_amount(goal['current_amount'])}")
        warning.setStyleSheet("color: #f44336;")
        layout.addWidget(warning)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                amount = float(amount_input.text())
                reason = reason_input.text()
                
                if not reason:
                    raise ValueError("Please provide a reason for the withdrawal")
                
                self.main_window.app.record_emergency_withdrawal(
                    goal_id=goal['id'],
                    amount=amount,
                    description=reason
                )
                
                self.main_window.show_success("Withdrawal recorded successfully")
                self.refresh_goals()
                
            except ValueError as e:
                self.main_window.show_error(str(e))
            except Exception as e:
                self.main_window.show_error(f"Error recording withdrawal: {str(e)}")

    def save_goal(self):
        """Save a new or updated goal."""
        try:
            name = self.name_input.text()
            amount = float(self.amount_input.text())
            description = self.description_input.text()
            target_date = self.date_input.date().toPyDate()
            priority = self.priority_select.currentText()
            goal_type = self.type_select.currentText()
            
            # Create allocation rule
            rule_type = self.rule_type.currentText()
            rule_value = self.rule_value.value()
            allocation_rules = {
                rule_type: rule_value if rule_type == 'percentage' else float(rule_value)
            }
            
            if goal_type == 'emergency_fund':
                try:
                    monthly_expenses = float(self.monthly_expenses_input.text())
                    months_coverage = self.months_coverage_input.value()
                    critical_threshold = self.threshold_input.value() / 100.0
                    
                    self.main_window.app.create_emergency_fund(
                        monthly_expenses=monthly_expenses,
                        months_coverage=months_coverage,
                        critical_threshold=critical_threshold,
                        allocation_rules=allocation_rules,
                        description=description
                    )
                except ValueError as e:
                    raise ValueError("Please enter valid monthly expenses")
            else:
                self.main_window.app.create_savings_goal(
                    name=name,
                    target_amount=amount,
                    description=description,
                    target_date=target_date,
                    priority=priority,
                    goal_type=goal_type,
                    allocation_rules=allocation_rules
                )
            
            self.main_window.show_success('Goal created successfully')
            self.goal_form.hide()
            self.refresh_goals()
            
        except ValueError as e:
            self.main_window.show_error(str(e))
        except Exception as e:
            self.main_window.show_error(f'Error creating goal: {str(e)}')
            
    def edit_goal(self, goal: dict):
        """Load a goal into the form for editing."""
        self.goal_form.show()
        self.name_input.setText(goal['name'])
        self.amount_input.setText(str(goal['target_amount']))
        self.description_input.setText(goal.get('description', ''))
        if goal['target_date']:
            self.date_input.setDate(QDate.fromString(goal['target_date'].strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.priority_select.setCurrentText(goal['priority'])
        self.type_select.setCurrentText(goal['goal_type'])
        
        if goal.get('allocation_rules'):
            rule = goal['allocation_rules']
            if 'percentage' in rule:
                self.rule_type.setCurrentText('percentage')
                self.rule_value.setValue(rule['percentage'])
            else:
                self.rule_type.setCurrentText('fixed_amount')
                self.rule_value.setValue(rule['fixed_amount'])
                
    def delete_goal(self, goal_id: int):
        """Delete a savings goal."""
        try:
            if self.main_window.app.delete_savings_goal(goal_id):
                self.main_window.show_success('Goal deleted successfully')
                self.refresh_goals()
            else:
                self.main_window.show_error('Failed to delete goal')
        except Exception as e:
            self.main_window.show_error(f'Error deleting goal: {str(e)}')
            
    def share_achievement(self, goal: dict):
        """Share goal achievement on social media."""
        try:
            # Prepare sharing message
            message = f"🎯 Goal Achievement Unlocked! 🎉\n\n"
            message += f"I just reached my savings goal: {goal['name']}\n"
            message += f"Target: {self.main_window.app.format_amount(goal['target_amount'])}\n"
            message += "\n#FinancialGoals #SavingsSuccess #PersonalFinance"
            
            # Create a dialog with sharing options
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit
            dialog = QDialog(self)
            dialog.setWindowTitle("Share Achievement")
            dialog_layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(message)
            dialog_layout.addWidget(text_edit)
            
            share_options = QHBoxLayout()
            
            twitter_btn = QPushButton("Share on Twitter")
            twitter_btn.clicked.connect(lambda: self.open_share_url(
                f"https://twitter.com/intent/tweet?text={message.replace(' ', '%20')}"
            ))
            share_options.addWidget(twitter_btn)
            
            linkedin_btn = QPushButton("Share on LinkedIn")
            linkedin_btn.clicked.connect(lambda: self.open_share_url(
                f"https://www.linkedin.com/sharing/share-offsite/?url=https://financeplanner.app&summary={message.replace(' ', '%20')}"
            ))
            share_options.addWidget(linkedin_btn)
            
            dialog_layout.addLayout(share_options)
            dialog.exec_()
            
        except Exception as e:
            self.main_window.show_error(f'Error sharing achievement: {str(e)}')
            
    def open_share_url(self, url: str):
        """Open URL in default browser."""
        from PyQt5.QtGui import QDesktopServices
        from PyQt5.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(url))
        
    def refresh_goals(self):
        """Refresh the goals grid."""
        try:
            # Clear current goals
            for i in reversed(range(self.goals_grid.count())):
                widget = self.goals_grid.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            try:
                # Get and filter goals
                goals = self.main_window.app.get_savings_goals(
                    include_completed=self.show_completed.isChecked()
                )
            except Exception as e:
                if "not logged in" in str(e).lower():
                    # Show login message
                    message = QLabel("Please log in to view and manage your savings goals")
                    message.setStyleSheet("""
                        QLabel {
                            font-size: 16px;
                            color: #666;
                            padding: 20px;
                            background-color: white;
                            border: 1px solid #ddd;
                            border-radius: 8px;
                            margin: 10px;
                        }
                    """)
                    message.setAlignment(Qt.AlignCenter)
                    self.goals_grid.addWidget(message, 0, 0, 1, 2)
                else:
                    raise e
                goals = []
            
            # Apply filters
            if self.priority_filter.currentText() != 'All':
                goals = [g for g in goals if g['priority'].lower() == self.priority_filter.currentText().lower()]
            
            if self.type_filter.currentText() != 'All':
                filter_type = self.type_filter.currentText().lower().replace('-', '_')
                goals = [g for g in goals if g['goal_type'] == filter_type]
            
            # Update charts
            self.update_charts(goals)
            
            # Display goals in grid
            row = col = 0
            max_cols = 2  # Display goals in 2 columns
            
            for goal in goals:
                self.goals_grid.addWidget(self.create_goal_widget(goal), row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                
        except Exception as e:
            self.main_window.show_error(f'Error refreshing goals: {str(e)}')
