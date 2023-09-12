from .api_repository import ApiRepository
"""
This class, Table, is responsible for interacting with a given API to fetch and process data related to tables. It provides functionalities to:

Retrieve all rows from a specified table.
Fetch specific fields for a table.
Identify and retrieve 'link_row' type fields for a table and for all tables in the provided data.
Additionally, it offers a verbose mode to print detailed messages during its operations.
"""
class TableRepository(ApiRepository):
    def get_all_rows_from_table(self, table_id):
        rows = []
        next_url = f"database/rows/table/{table_id}/"

        while next_url:
            response = self.api.request_response(next_url)
            data = self.api.handle_api_response(response)
            if not data:
                break
            rows.extend(data['results'])
            next_url = data['next']

        return rows
    
    def get_tables(self,table_ids):
        tables_data = {}
        for table_id in table_ids:
            table_data = self.get_all_rows_from_table(table_id.strip())
            tables_data[table_id] = table_data
        return tables_data

    def fetch_fields_for_table(self, table_id):
        response = self.api.request_response(f"database/fields/table/{table_id}/")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to fetch fields for table {table_id}. Status code: {response.status_code}")

    def get_link_fields_for_table(self, table_name):
        fields = self.fetch_fields_for_table(table_name)
        return [field for field in fields if field['type'] == 'link_row']
    
    def get_link_fields_for_all_tables(self, tables_data):
        link_fields = {}
        for table_name in tables_data:
            link_fields_for_table = self.get_link_fields_for_table(table_name)
            link_fields[table_name] = link_fields_for_table
        return link_fields
