"""Main application window."""

from PySide6.QtWidgets import QMainWindow, QWidget, QSplitter
from PySide6.QtCore import Qt
from gui.connection_panel import ConnectionPanel
from gui.table_browser import TableBrowser
from gui.query_editor import QueryEditor
from gui.results_display import ResultsDisplay
from db_manager.query_executor import QueryExecutor
from config import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_POS_X, WINDOW_POS_Y,
    LEFT_PANEL_WIDTH, RIGHT_PANEL_WIDTH
)


class MainWindow(QMainWindow):
    """Main application window orchestrating all components."""

    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_components()
        self.connect_signals()

    def setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(WINDOW_POS_X, WINDOW_POS_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

    def setup_components(self):
        """Initialize and layout UI components."""
        from PySide6.QtWidgets import QVBoxLayout

        # Left panel: connection and table browser
        self.connection_panel = ConnectionPanel()
        self.table_browser = TableBrowser()

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.connection_panel)
        left_layout.addWidget(self.table_browser)
        left_panel.setLayout(left_layout)

        # Right panel: query editor and results
        self.query_editor = QueryEditor()
        self.results_display = ResultsDisplay()

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.query_editor)
        right_layout.addWidget(self.results_display)
        right_panel.setLayout(right_layout)

        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([LEFT_PANEL_WIDTH, RIGHT_PANEL_WIDTH])

        self.setCentralWidget(splitter)

    def connect_signals(self):
        """Connect component signals."""
        self.connection_panel.connection_success.connect(self._on_connection_success)
        self.table_browser.table_selected.connect(self._on_table_selected)
        self.query_editor.execute_requested.connect(self._on_execute_query)

    def _on_connection_success(self, db_connection):
        """Handle successful database connection."""
        query_executor = QueryExecutor(db_connection.connection)
        self.results_display.set_query_executor(query_executor)

        # Get database name from the connection panel
        database_name = self.connection_panel.database_input.text()
        self.table_browser.load_tables(query_executor, database_name)

        self.query_editor.set_enabled(True)

    def _on_table_selected(self, table_name):
        """Handle table selection."""
        query = f"SELECT * FROM {table_name}"
        self.query_editor.set_query(query)

    def _on_execute_query(self, query):
        """Handle query execution request."""
        if self.connection_panel.is_connected():
            self.results_display.execute_query(query)
        else:
            self.results_display._show_status("Please connect to a database first", error=True)
