# SDBM — Simple Database Manager

A lightweight, user-friendly desktop GUI for managing MySQL databases. Browse tables, write SQL queries, and explore results—all without leaving the app.

Built with [PySide6](https://wiki.qt.io/Qt_for_Python) (Qt for Python).

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

Then:
1. **Connect**: Enter your MySQL host, user, password, and database name. Click **Connect**.
2. **Browse**: Click a table to load it, or write your own SQL query.
3. **Execute**: Click **Execute Query** to run it. Results appear in the table on the right.
4. **Scroll & Sort**: Scroll down to load more rows; click a column header to sort.

---

## Features

### Core Functionality
- ✅ **Database Connection** — Connect to MySQL with credentials (password masked)
- ✅ **Table Browser** — Browse available tables in the connected database
- ✅ **Query Editor** — Write and execute arbitrary SQL queries
- ✅ **Results Viewer** — Display query results in a sortable, resizable table

### Smart Loading & Sorting
- ✅ **Pagination** — Results load 1000 rows at a time for snappy UI
- ✅ **Auto-Load on Scroll** — Scroll to the bottom to fetch more rows
- ✅ **LIMIT Aware** — Respects your `LIMIT` clauses in queries
- ✅ **Column Sorting** — Click headers to sort ascending/descending
- ✅ **Resizable Columns** — Drag column borders to adjust width

### User Feedback
- ✅ **Status Indicator** — Visual red/green connection status
- ✅ **Row Counter** — See how many rows are loaded
- ✅ **Load Status** — Know when more rows can be fetched
- ✅ **Error Messages** — Clear feedback if something goes wrong

---

## Installation

### Requirements
- **Python 3.7+**
- **MySQL server** (local or remote)

### Steps

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Starting the Application
```bash
python main.py
```

The GUI opens with a two-panel layout:
- **Left panel**: Connection settings and table browser
- **Right panel**: Query editor and results display

### Connecting to a Database

1. In the left panel, fill in:
   - **Host**: MySQL server address (e.g., `localhost`, `192.168.1.100`)
   - **User**: Username (e.g., `root`)
   - **Password**: Your password (characters are masked)
   - **Database**: Database name to connect to

2. Click **Connect**. The status indicator turns green when connected.

### Browsing Tables

Once connected:
- Available tables appear in the **Tables** list below the connection settings
- Click any table to auto-populate a `SELECT * FROM <table>` query

### Running Queries

1. Write or paste SQL in the query editor on the right
2. Click **Execute Query** (or clear it with the **Clear** button)
3. For `SELECT` queries:
   - Results load in the table below
   - Scroll down to fetch more rows (up to 1000 at a time)
4. For other statements (`INSERT`, `UPDATE`, `DELETE`):
   - Success/error message appears in a dialog

### Sorting Results

- Click any column header to sort that column
- Click again to reverse direction (ascending ↔ descending)
- Sorting works on all currently loaded rows

---

## Project Structure

```
sdbm/
├── main.py                    # Application entry point
├── config.py                  # Centralized settings and constants
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── ARCHITECTURE.md            # Detailed design and extension guide
│
├── gui/                       # User interface components
│   ├── main_window.py         # Main window (orchestrates everything)
│   ├── connection_panel.py    # Database connection UI
│   ├── table_browser.py       # Table listing and selection
│   ├── query_editor.py        # SQL input and controls
│   └── results_display.py     # Query results with pagination & sorting
│
└── db_manager/                # Database abstraction layer
    ├── connection.py          # MySQL connection wrapper
    └── query_executor.py      # Query execution and result handling
```

---

## Architecture

SDBM uses a **modular, signal-based architecture** that makes the code easy to understand and extend.

### Key Design Patterns

**Component-Based**: Each UI element is a standalone component with a single responsibility:
- `ConnectionPanel` — manages database connections
- `TableBrowser` — displays available tables
- `QueryEditor` — handles SQL input
- `ResultsDisplay` — renders and paginates results

**Signal-Based Communication**: Components don't call each other directly. Instead, they emit signals that `MainWindow` listens to and responds to. This keeps components loosely coupled.

**Configuration Centralization**: All constants (window size, pagination settings, colors, etc.) live in `config.py`. Change one file, adjust the whole app.

### Component Flow

```
User connects to DB → ConnectionPanel emits "connection_success" 
   ↓
MainWindow receives signal → loads tables into TableBrowser
   ↓
User clicks a table → TableBrowser emits "table_selected"
   ↓
MainWindow receives signal → populates QueryEditor with "SELECT * FROM <table>"
   ↓
User clicks Execute → QueryEditor emits "execute_requested"
   ↓
MainWindow receives signal → sends query to ResultsDisplay
   ↓
ResultsDisplay executes query → displays results, waits for scroll
   ↓
User scrolls to bottom → ResultsDisplay emits signal → loads more rows
```

### Benefits

- **Testable**: Each component can be tested in isolation
- **Maintainable**: Changes to one component don't break others
- **Extensible**: Add new features without touching existing code
- **Readable**: Clear signal names make the flow obvious
- **Configurable**: Adjust behavior via `config.py`

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## Configuration

Edit `config.py` to customize the application:

```python
# Window settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# Data loading
RECORDS_PER_PAGE = 1000  # Increase for faster loading, decrease for better responsiveness

# Styling
APP_STYLE = 'Fusion'  # Qt style (try 'Windows', 'Macintosh', 'Android', etc.)
```

---

## Troubleshooting

### "Connection Failed" error
- **Check host/user/password**: Verify credentials in the connection fields
- **MySQL is running**: Ensure MySQL server is accessible at the specified host
- **Port issue**: Default port is 3306; if using a different port, modify `connection.py`

### "No connection or query!" message
- Click **Connect** first before running any queries
- Check that the connection status shows green

### Application is slow when loading large result sets
- Results load 1000 rows at a time. This is intentional—it keeps the UI responsive
- To adjust, edit `RECORDS_PER_PAGE` in `config.py`
- Reduce it (e.g., 500) for very large datasets to improve responsiveness

### Column header click does nothing
- Sorting only works on currently loaded rows in memory
- For server-side sorting over large datasets, see [ARCHITECTURE.md](./ARCHITECTURE.md) for extension ideas

### Can't enter password with special characters
- The password field treats all input as literal text—special characters are supported
- If connection fails, double-check the password is correct by comparing character-by-character

---

## Known Limitations

- **No credential persistence**: Connection settings are not saved between sessions. You'll re-enter them each time.
- **Client-side sorting**: Sorting works on loaded rows only, not the entire server-side result set. For very large datasets (millions of rows), server-side sorting is recommended.
- **Single database connection**: Only one active connection at a time. To query multiple databases, disconnect and reconnect.
- **Read-only for large operations**: Designed for ad-hoc queries, not bulk data operations. For large inserts/updates, consider using MySQL command line directly.

---

## Extending the Application

The modular architecture makes it easy to add features or modify behavior.

### Quick Examples

**Change pagination size:**
1. Edit `config.py`: `RECORDS_PER_PAGE = 500`
2. The change applies automatically.

**Add a new component:**
1. Create a new file in `gui/`
2. Inherit from `QWidget`
3. Emit signals for communication
4. Add to `main_window.py` and connect signals

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed extension patterns and testing strategies.
