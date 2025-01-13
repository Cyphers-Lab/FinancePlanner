#!/usr/bin/env python3
"""Entry point for the Financial Planner application."""
import os
from dotenv import load_dotenv
from src.cli import main

def setup_environment():
    """Set up the application environment."""
    # Load environment variables
    load_dotenv()
    
    # Create necessary directories
    os.makedirs("reports", exist_ok=True)
    
    # Ensure database directory exists
    db_url = os.getenv("DATABASE_URL", "sqlite:///financial_planner.db")
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

if __name__ == "__main__":
    setup_environment()
    main()
