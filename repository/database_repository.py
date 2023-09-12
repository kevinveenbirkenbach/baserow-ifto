from api_repository import ApiRepository
"""
This class, Database, is responsible for interacting with a given API to fetch and process data related to databases and tables. It provides functionalities to:

Fetch all tables associated with a given database.
Extract all data from a specified database.
Additionally, it offers a verbose mode to print detailed messages during its operations.

@Todo This is buggy and needs to be optimized
"""
class DatabaseRepository(ApiRepository):
    def get_all_tables_from_database(self, database_id):
        response = self.api.request_response(f"database/tables/database/{database_id}/")
        return self.api.handle_api_response(response) or []

    def get_all_data_from_database(self, database_id):
        tables = self.get_all_tables_from_database(database_id)
        data = {}

        for table in tables:
            table_id = table['id']
            table_name = table['name']
            data[table_name] = self.get_all_rows_from_table(table_id)

        return data