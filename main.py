import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the application style
    app.setStyle('Fusion')  # Set to Fusion style

    window = MainWindow()
    window.show()

    sys.exit(app.exec())