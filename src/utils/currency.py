"""Currency formatting utilities."""

def format_currency(amount: float, currency_symbol: str = '$') -> str:
    """Format a number as currency with the given symbol."""
    return f"{currency_symbol}{amount:.2f}"
