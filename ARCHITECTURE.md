# Architecture Guide

## Overview

SDBM follows a **modular, signal-based component architecture** that separates concerns between business logic and UI. This makes the codebase maintainable, testable, and easy to extend.

## Core Principles

1. **Single Responsibility**: Each component handles one specific aspect (connection, table browser, query editing, results display)
2. **Signal-Based Communication**: Components communicate through Qt signals rather than direct method calls
3. **Configuration Centralization**: All constants and settings are in `config.py`
4. **Business Logic Separation**: Database operations are isolated in `db_manager/`

## Component Overview

### `config.py`
Centralized configuration file. All magic numbers, constants, and settings go here.

**What goes here:**
- Window dimensions and positions
- Pagination settings (records per page)
- Application styling
- Database defaults

**When to modify:**
- Changing window size or behavior
- Adjusting pagination performance
- Adding new configuration options

---

### `gui/main_window.py`
**Role**: Orchestrator that ties all components together.

**Responsibilities:**
- Create and layout all UI components
- Connect component signals to slots
- Handle high-level application flow
- Manage component coordination

**Does NOT do:**
- Render tables
- Handle database connections directly
- Display queries

**Key methods:**
- `setup_window()`: Configure main window properties
- `setup_components()`: Initialize and layout all UI components
- `connect_signals()`: Wire up component communication
- Slots like `_on_connection_success()` coordinate between components

**Example: When user clicks a table:**
1. TableBrowser emits `table_selected` signal
2. MainWindow's `_on_table_selected()` slot receives it
3. MainWindow calls `query_editor.set_query()` to populate the editor

---

### `gui/connection_panel.py`
**Role**: Database connection UI and state management.

**Responsibilities:**
- Display connection input fields
- Validate user input
- Establish database connection
- Display connection status

**Signals:**
- `connection_success`: Emitted with the DatabaseConnection object when connection succeeds

**Key methods:**
- `connect_to_database()`: Attempt connection with user credentials
- `is_connected()`: Check current connection state
- `disconnect()`: Close current connection

**User flow:**
1. User fills in host, user, password, database
2. Clicks "Connect"
3. Component attempts connection via DatabaseConnection
4. On success: emits `connection_success` signal with the connection object
5. Visual status indicator updates (red/green)

---

### `gui/table_browser.py`
**Role**: Display and manage available database tables.

**Responsibilities:**
- Display list of tables from connected database
- Handle table selection
- Load tables via query executor

**Signals:**
- `table_selected`: Emitted with table name when user clicks a table

**Key methods:**
- `load_tables()`: Query database for list of tables
- `_on_table_clicked()`: Handle user selection

**User flow:**
1. User connects to database via ConnectionPanel
2. ConnectionPanel emits `connection_success`
3. MainWindow calls `table_browser.load_tables()`
4. TableBrowser queries `information_schema.tables`
5. User clicks a table
6. TableBrowser emits `table_selected` with table name

---

### `gui/query_editor.py`
**Role**: SQL query input interface.

**Responsibilities:**
- Display text editor for SQL input
- Provide execute/clear buttons
- Emit query execution requests

**Signals:**
- `execute_requested`: Emitted with query text when execute is clicked

**Key methods:**
- `get_query()`: Retrieve current query text
- `set_query()`: Populate editor with query
- `clear()`: Clear the editor
- `set_enabled()`: Enable/disable execute button

**User flow:**
1. User types or pastes SQL query
2. Clicks "Execute Query"
3. Emits `execute_requested` signal with query text
4. MainWindow receives signal and passes to ResultsDisplay

---

### `gui/results_display.py`
**Role**: Query results display with pagination and sorting.

**Responsibilities:**
- Execute queries and display results
- Implement lazy-loading pagination
- Handle column sorting
- Display status and error messages
- Manage pagination state

**State:**
- `local_data`: All loaded rows in memory
- `current_offset`: Current pagination offset
- `all_records_loaded`: Whether all results are in memory
- `current_sort_column`, `current_sort_order`: Sorting state

**Signals:**
- `loading_started`: Emitted when query execution begins
- `loading_completed`: Emitted with row count when first batch loads

**Key methods:**
- `set_query_executor()`: Inject the query executor dependency
- `execute_query()`: Run a query and display results
- `_load_data()`: Load next page of results (called on scroll)
- `_on_header_click()`: Handle sorting
- `_on_scroll()`: Handle pagination trigger

**Features:**
- **Lazy Loading**: Results load 1000 rows at a time; more load on scroll
- **Smart Limiting**: Respects `LIMIT` in the original query
- **Client-Side Sorting**: Sorts loaded rows by clicking column headers
- **Visual Feedback**: Status label shows row count and loading status

---

### `db_manager/connection.py`
**Role**: Database connection abstraction.

**Responsibilities:**
- Wrap mysql.connector for connection management
- Handle connection lifecycle
- Report connection status

**Key methods:**
- `connect()`: Establish connection to MySQL
- `close()`: Close connection
- Public: `connection` attribute (the actual mysql.connector.MySQLConnection)

---

### `db_manager/query_executor.py`
**Role**: Query execution abstraction.

**Responsibilities:**
- Execute parameterized queries safely
- Return results in a consistent format
- Distinguish between SELECT and non-SELECT queries

**Key methods:**
- `execute_query()`: Run a query, return (result, column_names)
  - For SELECT: result = rows (list of tuples), column_names = list
  - For others: result = message string, column_names = None

---

## Signal Flow Diagram

```
ConnectionPanel              TableBrowser           QueryEditor           ResultsDisplay
     |                           |                       |                      |
     |--connection_success----->MainWindow              |                      |
     |                           |                       |                      |
     |                           |---load_tables()------>|                      |
     |                           |                       |                      |
     |                           |<---emit table_selected|                      |
     |                           |                       |                      |
     |                           |<---set_query()--------|                      |
     |                           |                       |                      |
     |                           |                   execute_requested           |
     |                           |---execute_query()---->|                      |
     |                           |                       |                      |
     |                           |<---set_query_executor-|---execute_query()-->|
     |                           |                       |                      |
     |                           |                       |<--loading_completed--|
```

## How to Extend the Application

### Add a New Feature

**Example: Add database export to CSV**

1. Create `gui/export_panel.py` with an `ExportPanel` component
   - Emit `export_requested` signal with export options
2. In `main_window.py`:
   - Add `self.export_panel = ExportPanel()`
   - Connect `export_requested` to a new `_on_export()` slot
3. In `_on_export()`:
   - Use `self.results_display.local_data` to get current results
   - Implement CSV export logic
   - Optionally add an export method to `ResultsDisplay`

### Modify Results Display Behavior

**Example: Change pagination size**

1. Edit `config.py`: Update `RECORDS_PER_PAGE = 500`
2. `ResultsDisplay` will automatically use the new value

### Add Connection History

1. Create a new file `utils/config_store.py` for persistence
2. Modify `ConnectionPanel.connect_to_database()` to save credentials
3. Add a dropdown in `ConnectionPanel` to load saved connections

### Switch Database Type

1. Create `db_manager/postgres_connection.py` (similar interface to `connection.py`)
2. Create `db_manager/postgres_executor.py` (similar to `query_executor.py`)
3. Add configuration in `config.py` to select database type
4. In `ConnectionPanel.connect_to_database()`, conditionally use the right connection class

---

## Testing Strategy

Each component can be tested independently:

```python
# Test ConnectionPanel signals
def test_connection_panel_emits_success():
    panel = ConnectionPanel()
    spy = QtTest.QSignalSpy(panel.connection_success)
    panel.host_input.setText("localhost")
    # ... set other fields
    panel.connect_to_database()
    assert spy.count() == 1

# Test ResultsDisplay sorting
def test_results_sorting():
    display = ResultsDisplay()
    display.local_data = [(1, 'b'), (2, 'a')]
    display._on_header_click(1)  # Sort by column 1
    assert display.local_data == [(2, 'a'), (1, 'b')]
```

---

## Performance Considerations

1. **Pagination**: Results load 1000 rows at a time to avoid UI lag
2. **Client-Side Sorting**: Only sorts loaded rows; large datasets won't block UI
3. **Database Queries**: Uses parameterized queries to avoid SQL injection
4. **Memory**: All loaded rows kept in `ResultsDisplay.local_data` for sorting

For very large result sets (millions of rows), consider:
- Server-side sorting
- Reducing pagination size further
- Implementing server-side caching
