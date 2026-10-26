"""Table browser component for displaying available database tables."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PySide6.QtCore import pyqtSignal
from db_manager.query_executor import QueryExecutor


class TableBrowser(QWidget):
    """Component for browsing and selecting database tables."""

    table_selected = pyqtSignal(str)  # Emits selected table name

    def __init__(self):
        super().__init__()
        self.query_executor = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tables"))

        self.tables_list = QListWidget()
        self.tables_list.itemClicked.connect(self._on_table_clicked)
        layout.addWidget(self.tables_list)

        self.setLayout(layout)

    def load_tables(self, query_executor, database_name):
        """Load and display tables from the database."""
        self.query_executor = query_executor
        self.tables_list.clear()

        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema = %s"
            result, column_names = self.query_executor.execute_query(query, params=(database_name,))

            if column_names is not None and result:
                for table in result:
                    self.tables_list.addItem(table[0])
        except Exception as e:
            print(f"Error loading tables: {e}")

    def _on_table_clicked(self, item):
        """Handle table selection."""
        table_name = item.text()
        self.table_selected.emit(table_name)
