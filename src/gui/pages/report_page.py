"""Report generation page for the Financial Planner GUI."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QGridLayout, QComboBox,
                           QDateEdit, QTextEdit, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import os

class ReportPage(QWidget):
    """Report page for generating and viewing financial reports."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel('Financial Reports')
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
        
        # Left side - Report Generation Options
        left_panel = QVBoxLayout()
        
        # Report options form
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        form_layout = QGridLayout(form_frame)
        
        # Month selection
        form_layout.addWidget(QLabel('Month:'), 0, 0)
        self.month_select = QDateEdit()
        self.month_select.setDisplayFormat('MMMM yyyy')
        self.month_select.setDate(QDate.currentDate())
        form_layout.addWidget(self.month_select, 0, 1)
        
        # Report format selection
        form_layout.addWidget(QLabel('Format:'), 1, 0)
        self.format_select = QComboBox()
        self.format_select.addItems(['PDF', 'Text'])
        form_layout.addWidget(self.format_select, 1, 1)
        
        # Generate report button
        generate_btn = QPushButton('Generate Report')
        generate_btn.clicked.connect(self.generate_report)
        generate_btn.setStyleSheet("""
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
        form_layout.addWidget(generate_btn, 2, 0, 1, 2)
        
        # Export button
        export_btn = QPushButton('Export Report')
        export_btn.clicked.connect(self.export_report)
        export_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        form_layout.addWidget(export_btn, 3, 0, 1, 2)
        
        left_panel.addWidget(form_frame)
        
        # Report preview
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.StyledPanel)
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        
        preview_label = QLabel('Report Preview')
        preview_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        preview_layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: #f9f9f9;
            }
        """)
        preview_layout.addWidget(self.preview_text)
        
        left_panel.addWidget(preview_frame)
        content.addLayout(left_panel)
        
        # Right side - Historical Reports
        right_panel = QVBoxLayout()
        
        history_frame = QFrame()
        history_frame.setFrameStyle(QFrame.StyledPanel)
        history_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        history_layout = QVBoxLayout(history_frame)
        
        history_label = QLabel('Historical Reports')
        history_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        history_layout.addWidget(history_label)
        
        # Add historical report buttons
        self.history_layout = QVBoxLayout()
        history_layout.addLayout(self.history_layout)
        
        right_panel.addWidget(history_frame)
        content.addLayout(right_panel)
        
        # Add content to main layout
        layout.addLayout(content)
        
        # Load historical reports
        self.refresh_history()
        
    def generate_report(self):
        """Generate a new financial report."""
        try:
            month = self.month_select.date().toPyDate()
            output_format = self.format_select.currentText().lower()
            
            report_data = self.main_window.app.generate_monthly_report(
                month=month,
                output_format=output_format
            )
            
            if output_format == 'pdf':
                self.preview_text.setText('PDF report generated successfully.\nUse Export button to save the report.')
                self.current_report_path = report_data
            else:
                self.preview_text.setText(report_data)
                self.current_report_path = None
                
            self.main_window.show_success('Report generated successfully')
            self.refresh_history()
            
        except Exception as e:
            self.main_window.show_error(f'Error generating report: {str(e)}')
            
    def export_report(self):
        """Export the current report to a file."""
        try:
            if not hasattr(self, 'current_report_path') or not self.current_report_path:
                if not self.preview_text.toPlainText():
                    self.main_window.show_error('No report to export')
                    return
                    
                # Export text report
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    'Export Report',
                    os.path.expanduser('~/Documents'),
                    'Text Files (*.txt)'
                )
                
                if file_path:
                    with open(file_path, 'w') as f:
                        f.write(self.preview_text.toPlainText())
            else:
                # Export PDF report
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    'Export Report',
                    os.path.expanduser('~/Documents'),
                    'PDF Files (*.pdf)'
                )
                
                if file_path:
                    import shutil
                    shutil.copy2(self.current_report_path, file_path)
                    
            if file_path:
                self.main_window.show_success('Report exported successfully')
                
        except Exception as e:
            self.main_window.show_error(f'Error exporting report: {str(e)}')
            
    def load_historical_report(self, report_path):
        """Load a historical report for viewing."""
        try:
            if report_path.endswith('.pdf'):
                self.preview_text.setText('PDF report loaded.\nUse Export button to save the report.')
                self.current_report_path = report_path
            else:
                with open(report_path, 'r') as f:
                    self.preview_text.setText(f.read())
                self.current_report_path = None
                
        except Exception as e:
            self.main_window.show_error(f'Error loading report: {str(e)}')
            
    def refresh_history(self):
        """Refresh the list of historical reports."""
        try:
            # Clear existing history
            while self.history_layout.count():
                item = self.history_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                    
            # List reports directory
            reports_dir = os.path.join(os.getcwd(), 'reports')
            if os.path.exists(reports_dir):
                reports = sorted(
                    [f for f in os.listdir(reports_dir) if f.startswith('financial_report_')],
                    reverse=True
                )
                
                for report in reports:
                    report_path = os.path.join(reports_dir, report)
                    btn = QPushButton(report)
                    btn.clicked.connect(lambda p=report_path: self.load_historical_report(p))
                    btn.setStyleSheet("""
                        QPushButton {
                            padding: 8px;
                            background-color: #f5f5f5;
                            border: 1px solid #ddd;
                            border-radius: 4px;
                            text-align: left;
                        }
                        QPushButton:hover {
                            background-color: #e0e0e0;
                        }
                    """)
                    self.history_layout.addWidget(btn)
                    
        except Exception as e:
            self.main_window.show_error(f'Error refreshing history: {str(e)}')
