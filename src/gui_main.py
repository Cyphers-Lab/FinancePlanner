"""Main entry point for the Financial Planner GUI application."""
import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    """Initialize and launch the GUI application."""
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
