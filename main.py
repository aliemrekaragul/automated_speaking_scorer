import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """
    Main entry point for the Speaking Performance Scorer application.
    
    The application will:
    1. Launch the main scoring interface
    2. Allow configuration of API keys and task definitions through the UI
    3. Process audio files based on user selection
    
    Audio files should follow naming convention: YYMMDDXXX-S-tT.mp3
    Example: 231101013-6-t1.mp3
    """
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 