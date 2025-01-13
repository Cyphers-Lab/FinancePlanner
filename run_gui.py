"""Entry point for the Financial Planner GUI application."""
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.gui_main import main

if __name__ == '__main__':
    main()
