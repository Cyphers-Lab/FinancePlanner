"""Net worth tracking and management page for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QGridLayout, QLineEdit,
                           QComboBox, QTableWidget, QTableWidgetItem,
                           QHeaderView, QDialog, QDialogButtonBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')

from ...services.net_worth_service import NetWorthService
from ...models.models import AssetType

class NetWorthPage(QWidget):
    """Page for displaying and managing net worth information."""
    
    def __init__(self, main_window):
        """Initialize the net worth page."""
        super().__init__()
        self.main_window = main_window
        self.net_worth_service = NetWorthService(main_window.app.db)
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel('Net Worth Tracker')
        title.setStyleSheet('font-size: 24px; font-weight: bold;')
        header.addWidget(title)
        
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
        header.addStretch()
        header.addWidget(back_btn)
        layout.addLayout(header)
        
        # Main content area
        content = QHBoxLayout()
        
        # Left panel - Summary and Actions
        left_panel = QVBoxLayout()
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        
        self.net_worth_label = QLabel()
        self.net_worth_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        summary_layout.addWidget(self.net_worth_label)
        
        self.assets_label = QLabel()
        summary_layout.addWidget(self.assets_label)
        
        self.liabilities_label = QLabel()
        summary_layout.addWidget(self.liabilities_label)
        
        left_panel.addWidget(summary_frame)
        
        # Actions section
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.StyledPanel)
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        actions_layout = QVBoxLayout(actions_frame)
        
        add_asset_btn = QPushButton('Add Asset')
        add_asset_btn.clicked.connect(self.show_add_asset_dialog)
        add_asset_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        actions_layout.addWidget(add_asset_btn)
        
        add_goal_btn = QPushButton('Set Net Worth Goal')
        add_goal_btn.clicked.connect(self.show_add_goal_dialog)
        add_goal_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        actions_layout.addWidget(add_goal_btn)
        
        create_snapshot_btn = QPushButton('Create Snapshot')
        create_snapshot_btn.clicked.connect(self.create_snapshot)
        create_snapshot_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        actions_layout.addWidget(create_snapshot_btn)
        
        refresh_btn = QPushButton('Refresh Data')
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        actions_layout.addWidget(refresh_btn)
        
        left_panel.addWidget(actions_frame)
        content.addLayout(left_panel)
        
        # Right panel - Charts and Tables
        right_panel = QVBoxLayout()
        
        # Trend chart
        chart_frame = QFrame()
        chart_frame.setFrameStyle(QFrame.StyledPanel)
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        right_panel.addWidget(chart_frame)
        
        # Assets and Goals tables
        tables_frame = QFrame()
        tables_frame.setFrameStyle(QFrame.StyledPanel)
        tables_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        tables_layout = QVBoxLayout(tables_frame)
        
        # Assets table
        assets_label = QLabel('Assets')
        assets_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        tables_layout.addWidget(assets_label)
        
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(4)
        self.assets_table.setHorizontalHeaderLabels([
            'Name', 'Type', 'Value', 'Last Updated'
        ])
        self.assets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.assets_table.setStyleSheet("""
            QTableWidget {
                border: none;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #ddd;
            }
        """)
        tables_layout.addWidget(self.assets_table)
        
        # Goals table
        goals_label = QLabel('Goals')
        goals_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        tables_layout.addWidget(goals_label)
        
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(4)
        self.goals_table.setHorizontalHeaderLabels([
            'Description', 'Target Amount', 'Progress', 'Target Date'
        ])
        self.goals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.goals_table.setStyleSheet("""
            QTableWidget {
                border: none;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #ddd;
            }
        """)
        tables_layout.addWidget(self.goals_table)
        
        right_panel.addWidget(tables_frame)
        content.addLayout(right_panel)
        
        # Add content to main layout
        layout.addLayout(content)

    def refresh_data(self):
        """Refresh all displayed data."""
        try:
            # Get current user ID (implement based on your auth system)
            user_id = 1  # Placeholder
            
            # Update summary
            net_worth_data = self.net_worth_service.calculate_net_worth(user_id)
            self.update_summary(net_worth_data)
            
            # Update trend chart
            self.update_trend_chart(user_id)
            
            # Update assets table
            self.update_assets_table(user_id)
            
            # Update goals table
            self.update_goals_table(user_id)
            
        except Exception as e:
            self.main_window.show_error(f"Failed to refresh data: {str(e)}")

    def update_summary(self, net_worth_data):
        """Update the summary section with current net worth data."""
        self.net_worth_label.setText(f"Net Worth: ${net_worth_data['net_worth']:,.2f}")
        self.assets_label.setText(f"Total Assets: ${net_worth_data['total_assets']:,.2f}")
        self.liabilities_label.setText(f"Total Liabilities: ${net_worth_data['total_liabilities']:,.2f}")

    def update_trend_chart(self, user_id):
        """Update the net worth trend chart."""
        self.ax.clear()
        
        # Get historical data
        snapshots = self.net_worth_service.get_snapshots(user_id, limit=12)
        if not snapshots:
            self.ax.text(0.5, 0.5, 'No historical data available',
                        horizontalalignment='center',
                        verticalalignment='center')
        else:
            dates = [s.timestamp for s in snapshots]
            values = [s.net_worth for s in snapshots]
            
            self.ax.plot(dates, values, marker='o', color='#2196F3')
            self.ax.set_title('Net Worth Trend')
            self.ax.set_xlabel('Date')
            self.ax.set_ylabel('Net Worth ($)')
            self.ax.grid(True)
            
            # Rotate x-axis labels for better readability
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
            
            # Format y-axis labels as currency
            self.ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
            )
        
        self.figure.tight_layout()
        self.canvas.draw()

    def update_assets_table(self, user_id):
        """Update the assets table."""
        self.assets_table.setRowCount(0)
        assets = self.net_worth_service.get_user_assets(user_id)
        
        for asset in assets:
            row = self.assets_table.rowCount()
            self.assets_table.insertRow(row)
            
            self.assets_table.setItem(row, 0, QTableWidgetItem(asset.name))
            self.assets_table.setItem(row, 1, QTableWidgetItem(asset.type.value))
            self.assets_table.setItem(row, 2, QTableWidgetItem(f"${asset.value:,.2f}"))
            self.assets_table.setItem(
                row, 3, 
                QTableWidgetItem(asset.last_updated.strftime("%Y-%m-%d"))
            )

    def update_goals_table(self, user_id):
        """Update the goals table."""
        self.goals_table.setRowCount(0)
        goals = self.net_worth_service.get_active_goals(user_id)
        
        for goal in goals:
            row = self.goals_table.rowCount()
            self.goals_table.insertRow(row)
            
            progress = self.net_worth_service.check_goal_progress(goal.id)
            
            self.goals_table.setItem(row, 0, QTableWidgetItem(goal.description))
            self.goals_table.setItem(
                row, 1, 
                QTableWidgetItem(f"${goal.target_amount:,.2f}")
            )
            
            progress_item = QTableWidgetItem(f"{progress['progress_percentage']:.1f}%")
            progress_item.setForeground(
                Qt.green if progress['progress_percentage'] >= 100 else Qt.black
            )
            self.goals_table.setItem(row, 2, progress_item)
            
            self.goals_table.setItem(
                row, 3,
                QTableWidgetItem(goal.target_date.strftime("%Y-%m-%d"))
            )

    def show_add_asset_dialog(self):
        """Show dialog for adding a new asset."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Asset")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QGridLayout()
        
        # Name
        form_layout.addWidget(QLabel("Name:"), 0, 0)
        name_input = QLineEdit()
        form_layout.addWidget(name_input, 0, 1)
        
        # Type
        form_layout.addWidget(QLabel("Type:"), 1, 0)
        type_combo = QComboBox()
        type_combo.addItems([t.value for t in AssetType])
        form_layout.addWidget(type_combo, 1, 1)
        
        # Value
        form_layout.addWidget(QLabel("Value:"), 2, 0)
        value_input = QLineEdit()
        form_layout.addWidget(value_input, 2, 1)
        
        # Description
        form_layout.addWidget(QLabel("Description:"), 3, 0)
        desc_input = QLineEdit()
        form_layout.addWidget(desc_input, 3, 1)
        
        # Institution
        form_layout.addWidget(QLabel("Institution:"), 4, 0)
        inst_input = QLineEdit()
        form_layout.addWidget(inst_input, 4, 1)
        
        # Is Liquid
        form_layout.addWidget(QLabel("Is Liquid Asset:"), 5, 0)
        is_liquid_check = QComboBox()
        is_liquid_check.addItems(['No', 'Yes'])
        form_layout.addWidget(is_liquid_check, 5, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                # Get current user ID (implement based on your auth system)
                user_id = 1  # Placeholder
                
                asset_data = {
                    'name': name_input.text(),
                    'type': type_combo.currentText(),
                    'value': float(value_input.text()),
                    'description': desc_input.text(),
                    'institution': inst_input.text(),
                    'is_liquid': is_liquid_check.currentText() == 'Yes'
                }
                
                self.net_worth_service.add_asset(user_id, asset_data)
                self.refresh_data()
                self.main_window.show_success('Asset added successfully')
                
            except ValueError as e:
                self.main_window.show_error(str(e))

    def show_add_goal_dialog(self):
        """Show dialog for adding a new net worth goal."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Net Worth Goal")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QGridLayout()
        
        # Target amount
        form_layout.addWidget(QLabel("Target Amount:"), 0, 0)
        amount_input = QLineEdit()
        form_layout.addWidget(amount_input, 0, 1)
        
        # Target date
        form_layout.addWidget(QLabel("Target Date:"), 1, 0)
        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        date_input.setDate(QDate.currentDate().addYears(1))  # Default to 1 year from now
        form_layout.addWidget(date_input, 1, 1)
        
        # Description
        form_layout.addWidget(QLabel("Description:"), 2, 0)
        desc_input = QLineEdit()
        form_layout.addWidget(desc_input, 2, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                # Get current user ID (implement based on your auth system)
                user_id = 1  # Placeholder
                
                goal_data = {
                    'target_amount': float(amount_input.text()),
                    'target_date': date_input.date().toPyDate(),
                    'description': desc_input.text()
                }
                
                self.net_worth_service.add_goal(user_id, goal_data)
                self.refresh_data()
                self.main_window.show_success('Goal added successfully')
                
            except ValueError as e:
                self.main_window.show_error(str(e))

    def create_snapshot(self):
        """Create a new net worth snapshot."""
        try:
            # Get current user ID (implement based on your auth system)
            user_id = 1  # Placeholder
            
            self.net_worth_service.create_snapshot(user_id)
            self.refresh_data()
            self.main_window.show_success("Net worth snapshot created successfully")
            
        except Exception as e:
            self.main_window.show_error(f"Failed to create snapshot: {str(e)}")
