class QueryExecutor:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, query, limit=None, offset=None):
        if self.connection and query:
            paginated_query = query
            print(f"before: {paginated_query}")
            if limit is not None and offset is not None:
                paginated_query += f" LIMIT {limit} OFFSET {offset}"

            cursor = self.connection.cursor()
            try:
                cursor.execute(paginated_query)
                if paginated_query.strip().lower().startswith("select"):
                    result = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    return result, column_names  # Return data and column names
                else:
                    self.connection.commit()
                    return "Query executed successfully!", None  # Return success message and None for columns
            except Exception as err:
                return f"Error: {err}", None  # Return error message and None for columns
        return "No connection or query!", None  # Return error message and None for columns
