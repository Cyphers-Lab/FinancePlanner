# Financial Planner

A comprehensive Python application for personal financial management and planning. This application helps users track budgets, expenses, investments, and debts while providing insights into their financial health.

## Features

- **Budget Management**
  - Create and track monthly budgets by category
  - Monitor spending against budgets
  - Receive alerts when spending exceeds thresholds

- **Expense Tracking**
  - Record daily expenses
  - Automatic categorization of recurring expenses
  - Detailed expense analysis and reporting

- **Investment Portfolio**
  - Track stocks and cryptocurrency investments
  - Real-time portfolio valuation
  - Performance analysis and reporting
  - Integration with Alpha Vantage API for market data

- **Debt Management**
  - Track multiple debts and loans
  - Calculate optimal payment strategies (snowball/avalanche methods)
  - Monitor debt reduction progress

- **Financial Health**
  - Calculate overall financial health score
  - Receive personalized insights and recommendations
  - Track progress over time

- **Reporting**
  - Generate detailed financial reports
  - Export data to PDF format
  - Visualize financial trends with charts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/FinancePlanner.git
cd FinancePlanner
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` file and add your configuration:
- Set your preferred database URL (default: SQLite)
- Generate and set a secure SECRET_KEY
- Add your Alpha Vantage API key for investment tracking

## Usage

1. Start the application:
```bash
python main.py
```

2. First-time setup:
- Register a new account
- Set up your initial budget categories
- Add any existing investments or debts

3. Regular usage:
- Track daily expenses
- Monitor budget compliance
- Review investment performance
- Generate financial reports
- Check financial health score

## Example Usage

### Creating a Budget

```
1. Select "Budget Management" from the main menu
2. Choose "Create Budget Category"
3. Enter category name (e.g., "Groceries")
4. Enter monthly budget amount
```

### Recording an Expense

```
1. Select "Transactions" from the main menu
2. Choose "Add Expense"
3. Enter amount and category
4. Add optional description
```

### Adding an Investment

```
1. Select "Investments" from the main menu
2. Choose "Add Investment"
3. Select investment type (stock/crypto)
4. Enter symbol and purchase details
```

### Generating Reports

```
1. Select "Reports" from the main menu
2. Choose "Generate Monthly Report"
3. Reports are saved in the 'reports' directory
```

## Project Structure

```
FinancePlanner/
├── src/
│   ├── models/
│   │   ├── base.py
│   │   └── models.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── budget_service.py
│   │   ├── transaction_service.py
│   │   ├── investment_service.py
│   │   ├── debt_service.py
│   │   └── report_service.py
│   ├── app.py
│   └── cli.py
├── main.py
├── requirements.txt
└── .env.example
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 coding standards. To check code style:

```bash
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Alpha Vantage API for market data
- SQLAlchemy for database management
- Click for CLI interface
- Matplotlib and Seaborn for data visualization
