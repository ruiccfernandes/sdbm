import re
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QTableView, QHeaderView, QSplitter, QLabel, QLineEdit, QListWidget, QHBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from db_manager.connection import DatabaseConnection
from db_manager.query_executor import QueryExecutor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize variables for pagination and sorting
        self.records_per_page = 1000
        self.current_offset = 0
        self.user_limit = None  # To hold user-defined limit
        self.total_loaded = 0  # To track total loaded records
        self.all_records_loaded = False  # To check if all records are loaded
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder
        self.local_data = []  # Local storage for data

        # Setup UI
        self.setWindowTitle("Simple Database Manager")
        self.setGeometry(100, 100, 1000, 600)

        # Create a QSplitter to divide the window into two resizable sections (left and right)
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Database connection and table listing
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Connection settings (just placeholders)
        self.host_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.database_input = QLineEdit()

        self.host_input.setPlaceholderText("Host")
        self.user_input.setPlaceholderText("User")
        self.password_input.setPlaceholderText("Password")
        self.database_input.setPlaceholderText("Database")

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_database)

        left_layout.addWidget(QLabel("Database Connection"))
        left_layout.addWidget(self.host_input)
        left_layout.addWidget(self.user_input)
        left_layout.addWidget(self.password_input)
        left_layout.addWidget(self.database_input)
        left_layout.addWidget(self.connect_button)

        # Table listing
        self.tables_list = QListWidget()
        self.tables_list.itemClicked.connect(self.table_selected)
        left_layout.addWidget(QLabel("Tables"))
        left_layout.addWidget(self.tables_list)

        left_panel.setLayout(left_layout)

        # Right panel: Query editor and results display
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # SQL Query input
        self.query_text = QTextEdit()
        right_layout.addWidget(self.query_text)

        # Execute Query Button
        self.execute_button = QPushButton("Execute Query")
        self.execute_button.clicked.connect(self.execute_query)
        right_layout.addWidget(self.execute_button)

        # Table for displaying results
        self.results_table = QTableView()
        right_layout.addWidget(self.results_table)

        # Model for displaying data
        self.model = QStandardItemModel(self)
        self.results_table.setModel(self.model)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Scroll detection for lazy loading
        self.results_table.verticalScrollBar().valueChanged.connect(self.on_scroll)

        # Header click detection for sorting
        self.results_table.horizontalHeader().sectionClicked.connect(self.on_header_click)

        right_panel.setLayout(right_layout)

        # Add the left and right panels to the splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 800])  # Set initial sizes

        # Set the splitter as the central widget
        self.setCentralWidget(splitter)

        # Initialize the DatabaseConnection object (to be set later)
        self.db_connection = None
        self.query_executor = None

    def connect_to_database(self):
        """Connect to the database using user input and populate the table list."""
        host = self.host_input.text()
        user = self.user_input.text()
        password = self.password_input.text()
        database = self.database_input.text()

        # Establish the connection
        self.db_connection = DatabaseConnection()
        self.db_connection.connect(host=host, user=user, password=password, database=database)
        self.query_executor = QueryExecutor(self.db_connection.connection)

        # Get the list of tables
        query = (f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{database}'")
        result, _ = self.query_executor.execute_query(query)

        # Populate the tables list
        self.tables_list.clear()
        if result:
            for table in result:
                self.tables_list.addItem(table[0])

    def table_selected(self, item):
        """Handle table selection from the list and display the selected table."""
        table_name = item.text()
        self.query_text.setText(f"SELECT * FROM {table_name}")

    def execute_query(self, append=False):
        """Execute query and load data into the table."""
        query = self.query_text.toPlainText()

        # Extract LIMIT if present
        limit_match = re.search(r'\bLIMIT\s+(\d+)', query, flags=re.IGNORECASE)
        if limit_match:
            self.user_limit = int(limit_match.group(1))
        else:
            self.user_limit = float('inf')  # Default to no limit if not specified

        # Remove existing LIMIT and OFFSET from the query
        query = re.sub(r'\s*LIMIT\s+\d+', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\s*OFFSET\s+\d+', '', query, flags=re.IGNORECASE)

        # Calculate the effective offset based on loading mode
        effective_offset = self.current_offset if append else 0

        # Append LIMIT and OFFSET to the query for loading
        limit_to_load = min(self.records_per_page, self.user_limit - self.total_loaded) if not append else self.records_per_page
        if limit_to_load > 0:  # Only load if there's still data to load
            query = f"{query} LIMIT {limit_to_load} OFFSET {effective_offset}"

            # Fetch records with limit and offset
            result, column_names = self.query_executor.execute_query(query)

            # Check if we reached the user limit
            if result:
                # If it's the initial load, set column names
                if self.model.rowCount() == 0 and column_names:
                    self.model.setColumnCount(len(column_names))
                    self.model.setHorizontalHeaderLabels(column_names)

                # Append new rows to the local data
                self.local_data.extend(result)

                # Populate the table with results
                row_start = self.model.rowCount() if append else 0
                self.model.setRowCount(row_start + len(result))

                for row_index, row_data in enumerate(result, start=row_start):
                    for column_index, value in enumerate(row_data):
                        item = QStandardItem(str(value))
                        # Ensure numerical values are set for sorting
                        if isinstance(value, (int, float)):
                            item.setData(value, Qt.EditRole)
                        self.model.setItem(row_index, column_index, item)

                # Update the offsets and count
                self.current_offset += len(result)
                self.total_loaded += len(result)

                # Check if we've reached the user limit
                if self.total_loaded >= self.user_limit:
                    self.all_records_loaded = True
            else:
                # No result means all records have been loaded
                self.all_records_loaded = True

    def on_scroll(self):
        """Detect when the user scrolls to the bottom and load more records."""
        if self.all_records_loaded:
            return

        scrollbar = self.results_table.verticalScrollBar()
        if scrollbar.value() == scrollbar.maximum():
            # User scrolled to the bottom, load more records
            self.execute_query(append=True)

    def on_header_click(self, index):
        """Handle sorting when a column header is clicked."""
        # Determine the current sorting order
        if self.current_sort_column == index:
            self.current_sort_order = Qt.DescendingOrder if self.current_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.current_sort_column = index
            self.current_sort_order = Qt.AscendingOrder

        # Disable sorting temporarily while we reload
        self.results_table.setSortingEnabled(False)

        # Sort the local data
        self.local_data.sort(key=lambda x: x[self.current_sort_column], reverse=self.current_sort_order == Qt.DescendingOrder)

        # Clear the model and repopulate it with sorted data
        self.model.setRowCount(0)  # Clear the model

        for row_data in self.local_data:
            row_items = []
            for value in row_data:
                item = QStandardItem(str(value))
                if isinstance(value, (int, float)):
                    item.setData(value, Qt.EditRole)  # Use numerical value for sorting
                row_items.append(item)
            self.model.appendRow(row_items)

        # Re-enable sorting
        self.results_table.setSortingEnabled(True)
