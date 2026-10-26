"""Query editor component for SQL input and execution."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QHBoxLayout
from PySide6.QtCore import pyqtSignal


class QueryEditor(QWidget):
    """Component for editing and executing SQL queries."""

    execute_requested = pyqtSignal(str)  # Emits query text

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        layout.addWidget(QLabel("SQL Query"))

        self.query_text = QTextEdit()
        self.query_text.setPlaceholderText("Enter SQL query here...")
        layout.addWidget(self.query_text)

        # Button layout
        button_layout = QHBoxLayout()
        self.execute_button = QPushButton("Execute Query")
        self.execute_button.clicked.connect(self._on_execute_clicked)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)

        button_layout.addWidget(self.execute_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def set_query(self, query):
        """Set the query text."""
        self.query_text.setText(query)

    def get_query(self):
        """Get the current query text."""
        return self.query_text.toPlainText()

    def clear(self):
        """Clear the query editor."""
        self.query_text.clear()

    def _on_execute_clicked(self):
        """Handle execute button click."""
        query = self.get_query().strip()
        if query:
            self.execute_requested.emit(query)

    def set_enabled(self, enabled):
        """Enable or disable the execute button."""
        self.execute_button.setEnabled(enabled)
