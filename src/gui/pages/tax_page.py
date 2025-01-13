"""Tax planning page for the Financial Planner application."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QLineEdit, QPushButton, QTreeWidget, 
                           QTreeWidgetItem, QGroupBox, QDialog, QTextEdit,
                           QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from datetime import datetime

from ...models.models import EmploymentType, TaxCategory, Transaction
from ...services.tax_service import TaxService

class TaxPage(QWidget):
    """Tax planning page allowing users to manage tax profiles and categorize transactions."""

    def __init__(self, main_window):
        """Initialize the tax planning page."""
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        # Initialize class attributes
        self.user_id = self.main_window.app.current_user.id if self.main_window and self.main_window.app.current_user else None
        self.tax_service = TaxService(self.main_window.app.db if self.main_window else None)
        self.current_year = datetime.now().year
        self.current_profile = None
        layout = QVBoxLayout()
        
        # Header with back button
        header = QHBoxLayout()
        title = QLabel('Tax Planning')
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
        
        # Profile Section
        profile_group = QGroupBox("Tax Profile")
        profile_layout = QFormLayout()
        
        # Employment Type
        self.employment_type_combo = QComboBox()
        self.employment_type_combo.addItems([e.value for e in EmploymentType])
        profile_layout.addRow("Employment Type:", self.employment_type_combo)
        
        # Filing Status
        self.filing_status_combo = QComboBox()
        self.filing_status_combo.addItems([
            "single", "married_joint", "married_separate", "head_of_household"
        ])
        profile_layout.addRow("Filing Status:", self.filing_status_combo)
        
        # Tax Rate
        self.tax_rate_edit = QLineEdit()
        profile_layout.addRow("Tax Rate (%):", self.tax_rate_edit)
        
        # Save Profile Button
        self.save_profile_btn = QPushButton("Save Profile")
        self.save_profile_btn.clicked.connect(self.save_profile)
        profile_layout.addRow(self.save_profile_btn)
        
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)
        
        # Transactions Section
        transactions_group = QGroupBox("Tax Categories")
        transactions_layout = QVBoxLayout()
        
        # Transactions Tree
        self.transactions_tree = QTreeWidget()
        self.transactions_tree.setHeaderLabels([
            "Date", "Description", "Amount", "Category", "Tax Category"
        ])
        self.transactions_tree.setColumnWidth(0, 100)
        self.transactions_tree.setColumnWidth(1, 200)
        self.transactions_tree.setColumnWidth(2, 100)
        self.transactions_tree.setColumnWidth(3, 100)
        self.transactions_tree.setColumnWidth(4, 100)
        self.transactions_tree.itemDoubleClicked.connect(self.on_transaction_double_click)
        
        transactions_layout.addWidget(self.transactions_tree)
        transactions_group.setLayout(transactions_layout)
        layout.addWidget(transactions_group)
        
        # Reports Section
        reports_group = QGroupBox("Tax Reports")
        reports_layout = QVBoxLayout()
        
        self.generate_report_btn = QPushButton("Generate Tax Report")
        self.generate_report_btn.clicked.connect(self.generate_report)
        reports_layout.addWidget(self.generate_report_btn)
        
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)
        
        self.setLayout(layout)

    def load_tax_profile(self):
        """Load the user's tax profile for the current year."""
        if not self.user_id:
            return
            
        self.current_profile = self.tax_service.get_tax_profile(
            self.user_id, 
            self.current_year
        )
        
        if self.current_profile:
            self.employment_type_combo.setCurrentText(
                self.current_profile.employment_type.value
            )
            self.filing_status_combo.setCurrentText(self.current_profile.filing_status)
            rate = (
                self.current_profile.withholding_rate 
                if self.current_profile.employment_type == EmploymentType.PAYEE
                else self.current_profile.estimated_tax_rate
            )
            self.tax_rate_edit.setText(str(rate * 100 if rate else ""))

    def save_profile(self):
        """Save the tax profile."""
        if not self.user_id:
            return
            
        try:
            employment_type = EmploymentType(self.employment_type_combo.currentText())
            filing_status = self.filing_status_combo.currentText()
            tax_rate = float(self.tax_rate_edit.text()) / 100

            self.tax_service.create_tax_profile(
                user_id=self.user_id,
                employment_type=employment_type,
                tax_year=self.current_year,
                filing_status=filing_status,
                withholding_rate=tax_rate if employment_type == EmploymentType.PAYEE else None,
                estimated_tax_rate=tax_rate if employment_type != EmploymentType.PAYEE else None
            )
            QMessageBox.information(self, "Success", "Tax profile saved successfully!")
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save profile: {str(e)}")

    def load_transactions(self):
        """Load transactions for the current year."""
        if not self.user_id:
            return
            
        self.transactions_tree.clear()
        
        transactions = self.tax_service.get_uncategorized_transactions(
            self.user_id,
            self.current_year
        )
        
        for transaction in transactions:
            item = QTreeWidgetItem([
                transaction.date.strftime("%Y-%m-%d"),
                transaction.description,
                f"${transaction.amount:.2f}",
                transaction.category,
                transaction.tax_category.value if transaction.tax_category else "Uncategorized"
            ])
            item.setData(0, Qt.UserRole, transaction.id)
            self.transactions_tree.addTopLevelItem(item)

    def on_transaction_double_click(self, item, column):
        """Handle double-click on transaction."""
        transaction_id = item.data(0, Qt.UserRole)
        dialog = TaxCategoryDialog(self, transaction_id, self.tax_service)
        if dialog.exec_() == QDialog.Accepted:
            self.load_transactions()

    def generate_report(self):
        """Generate and display tax report."""
        if not self.user_id:
            return
            
        try:
            if not self.current_profile:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Please set up your tax profile before generating a report."
                )
                return

            report = self.tax_service.generate_tax_report(
                self.user_id,
                self.current_year
            )
            
            # Show report summary
            summary = report.report_data
            QMessageBox.information(
                self,
                "Tax Report Summary",
                f"Tax Year: {self.current_year}\n\n"
                f"Total Income: ${summary['summary']['total_income']:.2f}\n"
                f"Total Deductions: ${summary['summary']['total_deductible_expenses']:.2f}\n"
                f"Taxable Income: ${summary['calculations']['taxable_income']:.2f}\n"
                f"Estimated Tax: ${summary['calculations']['estimated_tax']:.2f}\n"
                f"Tax Credits: ${summary['calculations']['tax_credits']:.2f}\n"
                f"Final Tax Liability: ${summary['calculations']['final_tax_liability']:.2f}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def refresh_data(self):
        """Refresh page data."""
        self.load_tax_profile()
        self.load_transactions()

class TaxCategoryDialog(QDialog):
    """Dialog for categorizing transactions for tax purposes."""

    def __init__(self, parent, transaction_id: int, tax_service: TaxService):
        """Initialize the tax category dialog."""
        super().__init__(parent)
        self.transaction_id = transaction_id
        self.tax_service = tax_service
        
        self.setWindowTitle("Tax Category")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QFormLayout()
        
        # Tax Category
        self.category_combo = QComboBox()
        self.category_combo.addItems([c.value for c in TaxCategory])
        layout.addRow("Tax Category:", self.category_combo)
        
        # Deductible Amount
        self.amount_edit = QLineEdit()
        layout.addRow("Deductible Amount:", self.amount_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        layout.addRow("Notes:", self.notes_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_category)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)

    def save_category(self):
        """Save the tax category for the transaction."""
        try:
            tax_category = TaxCategory(self.category_combo.currentText())
            deductible_amount = (
                float(self.amount_edit.text()) if self.amount_edit.text() else None
            )
            notes = self.notes_edit.toPlainText()
            
            self.tax_service.categorize_transaction(
                self.transaction_id,
                tax_category,
                deductible_amount,
                notes
            )
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save category: {str(e)}")
