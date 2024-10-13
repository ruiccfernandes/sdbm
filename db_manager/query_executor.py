class QueryExecutor:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, query):
        if self.connection and query:
            cursor = self.connection.cursor()
            print(query)
            try:
                cursor.execute(query)
                if query.strip().lower().startswith("select"):
                    result = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    return result, column_names  # Return data and column names
                else:
                    self.connection.commit()
                    return "Query executed successfully!", None  # Return success message and None for columns
            except Exception as err:
                return f"Error: {err}", None  # Return error message and None for columns
        return "No connection or query!", None  # Return error message and None for columns
