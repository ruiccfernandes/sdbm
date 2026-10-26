"""Results display component for showing query results in a table."""

import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QLabel, QMessageBox
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, pyqtSignal
from db_manager.query_executor import QueryExecutor
from config import RECORDS_PER_PAGE


class ResultsDisplay(QWidget):
    """Component for displaying query results in a table with sorting and pagination."""

    loading_started = pyqtSignal()
    loading_completed = pyqtSignal(int)  # Emits row count

    def __init__(self):
        super().__init__()

        # State
        self.query_executor = None
        self.records_per_page = RECORDS_PER_PAGE
        self.current_offset = 0
        self.user_limit = None
        self.total_loaded = 0
        self.all_records_loaded = False
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder
        self.local_data = []
        self.original_query = ""

        self.setup_ui()

    def setup_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Results table
        self.results_table = QTableView()
        self.model = QStandardItemModel(self)
        self.results_table.setModel(self.model)

        # Table configuration
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.sectionClicked.connect(self._on_header_click)

        # Pagination via scrollbar
        self.results_table.verticalScrollBar().valueChanged.connect(self._on_scroll)

        layout.addWidget(self.results_table)
        self.setLayout(layout)

    def set_query_executor(self, query_executor):
        """Set the query executor."""
        self.query_executor = query_executor

    def execute_query(self, query):
        """Execute a query and display results."""
        if not self.query_executor:
            self._show_status("No database connection", error=True)
            return

        self._reset_state()
        self.original_query = query
        self.loading_started.emit()
        self._load_data()

    def _load_data(self):
        """Load data from the database with pagination."""
        if self.all_records_loaded or not self.query_executor:
            return

        query = self._build_paginated_query(self.original_query)

        try:
            result, column_names = self.query_executor.execute_query(query)

            if column_names is None:
                # Non-SELECT statement
                self.all_records_loaded = True
                if isinstance(result, str) and result.lower().startswith("error"):
                    self._show_status(result, error=True)
                    QMessageBox.critical(self, "Query Error", result)
                else:
                    self._show_status(f"Executed: {result}")
                    QMessageBox.information(self, "Success", str(result))
                return

            if result:
                if self.model.rowCount() == 0:
                    self.model.setColumnCount(len(column_names))
                    self.model.setHorizontalHeaderLabels(column_names)

                self.local_data.extend(result)
                row_start = self.model.rowCount()
                self.model.setRowCount(row_start + len(result))

                for row_index, row_data in enumerate(result, start=row_start):
                    for column_index, value in enumerate(row_data):
                        item = QStandardItem(str(value))
                        if isinstance(value, (int, float)):
                            item.setData(value, Qt.EditRole)
                        self.model.setItem(row_index, column_index, item)

                self.current_offset += len(result)
                self.total_loaded += len(result)

                if self.total_loaded >= self.user_limit:
                    self.all_records_loaded = True

                self._update_status()
            else:
                self.all_records_loaded = True
                self._update_status()

            self.loading_completed.emit(self.model.rowCount())

        except Exception as e:
            self._show_status(f"Error: {str(e)}", error=True)
            QMessageBox.critical(self, "Query Error", str(e))

    def _build_paginated_query(self, query):
        """Add LIMIT and OFFSET to query for pagination."""
        # Extract LIMIT if present
        limit_match = re.search(r'\bLIMIT\s+(\d+)', query, flags=re.IGNORECASE)
        if limit_match:
            self.user_limit = int(limit_match.group(1))
        else:
            self.user_limit = float('inf')

        # Remove existing LIMIT and OFFSET
        query = re.sub(r'\s*LIMIT\s+\d+', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\s*OFFSET\s+\d+', '', query, flags=re.IGNORECASE)

        # Calculate limit to load
        limit_to_load = min(self.records_per_page, self.user_limit - self.total_loaded)
        if limit_to_load > 0:
            query = f"{query} LIMIT {limit_to_load} OFFSET {self.current_offset}"

        return query

    def _reset_state(self):
        """Reset all state variables."""
        self.model.clear()
        self.model.setRowCount(0)
        self.local_data.clear()
        self.current_offset = 0
        self.total_loaded = 0
        self.all_records_loaded = False
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder

    def _on_scroll(self):
        """Handle scroll to bottom for lazy loading."""
        if self.all_records_loaded:
            return

        scrollbar = self.results_table.verticalScrollBar()
        if scrollbar.value() == scrollbar.maximum():
            self._load_data()

    def _on_header_click(self, index):
        """Handle column header click for sorting."""
        if self.current_sort_column == index:
            self.current_sort_order = Qt.DescendingOrder if self.current_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.current_sort_column = index
            self.current_sort_order = Qt.AscendingOrder

        self.results_table.setSortingEnabled(False)

        self.local_data.sort(
            key=lambda x: ('' if x[self.current_sort_column] is None else x[self.current_sort_column]),
            reverse=self.current_sort_order == Qt.DescendingOrder
        )

        self.model.setRowCount(0)
        for row_data in self.local_data:
            row_items = []
            for value in row_data:
                item = QStandardItem(str(value))
                if isinstance(value, (int, float)):
                    item.setData(value, Qt.EditRole)
                row_items.append(item)
            self.model.appendRow(row_items)

        self.results_table.setSortingEnabled(True)

    def _update_status(self):
        """Update status label with current load info."""
        status = f"Loaded: {self.model.rowCount()} rows"
        if not self.all_records_loaded:
            status += " (scroll for more)"
        self._show_status(status)

    def _show_status(self, message, error=False):
        """Display status message."""
        self.status_label.setText(message)
        if error:
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setStyleSheet("color: green;")

    def clear(self):
        """Clear the results display."""
        self._reset_state()
        self._show_status("Ready")
