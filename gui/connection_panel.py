"""Database connection panel UI component."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt, pyqtSignal
from db_manager.connection import DatabaseConnection


class ConnectionPanel(QWidget):
    """Panel for database connection settings."""

    connection_success = pyqtSignal(object)  # Emits DatabaseConnection object

    def __init__(self):
        super().__init__()
        self.db_connection = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Connection title
        layout.addWidget(QLabel("Database Connection"))

        # Input fields
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Host")
        self.host_input.setText("localhost")

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("User")
        self.user_input.setText("root")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText("Database")

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_database)

        layout.addWidget(self.host_input)
        layout.addWidget(self.user_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.database_input)
        layout.addWidget(self.connect_button)

        # Status indicator
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)

        layout.addStretch()
        self.setLayout(layout)

    def connect_to_database(self):
        """Attempt to connect to the database."""
        host = self.host_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text()
        database = self.database_input.text().strip()

        if not all([host, user, database]):
            QMessageBox.warning(self, "Validation Error", "Please fill in all required fields.")
            return

        self.connect_button.setEnabled(False)
        self.connect_button.setText("Connecting...")

        try:
            self.db_connection = DatabaseConnection()
            if self.db_connection.connect(host=host, user=user, password=password, database=database):
                self.status_label.setText(f"Connected to {database}")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.connection_success.emit(self.db_connection)
            else:
                self._show_error("Could not connect to the database. Please check your credentials.")
        except Exception as e:
            self._show_error(f"Connection error: {str(e)}")
        finally:
            self.connect_button.setEnabled(True)
            self.connect_button.setText("Connect")

    def _show_error(self, message):
        """Display error message and update status."""
        QMessageBox.critical(self, "Connection Failed", message)
        self.status_label.setText("Connection Failed")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.db_connection = None

    def is_connected(self):
        """Check if currently connected."""
        return self.db_connection is not None

    def disconnect(self):
        """Disconnect from database."""
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
