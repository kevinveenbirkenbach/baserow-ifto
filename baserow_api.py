import requests
import json

class BaserowAPI:
    def __init__(self, base_url, api_key, verbose=False):
        self.base_url = base_url
        self.api_key = api_key
        self.verbose = verbose
        self.headers = create_headers(self)
        self.print_verbose_message("Headers:", headers)

    def create_headers(self):
        """Create headers for API requests."""
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def print_verbose_message(self, message):
        if self.verbose:
            print(message)

    def handle_api_response(self, response):
        """Handle API response, check for errors and decode JSON."""
        self.print_verbose_message("[INFO] Handling API response...")
        self.print_verbose_message("Response Status Code:", response.status_code)
        self.print_verbose_message("Response Headers:", response.headers)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from Baserow API.")
            print("Response content:", response.content.decode())
            return None

        try:
            return response.json()
        except requests.RequestsJSONDecodeError:
            print("Error: Failed to decode the response as JSON.")
            return None

    def get_all_rows_from_table(self, table_id):
        if self.verbose:
            print(f"[INFO] Fetching all rows from table with ID: {table_id}...")
        rows = []
        next_url = "database/rows/table/{table_id}/"

        while next_url:
            request_response(next_url)
            self.print_verbose_message("Requesting:", next_url)
            data = self.handle_api_response(response)
            if not data:
                break
            rows.extend(data['results'])
            next_url = data['next']

        return rows

    def request_response(self,command):
        return requests.get(f"{self.base_url}{command}", headers=self.headers)

    def get_all_tables_from_database(self, database_id):
        self.print_verbose_message("[INFO] Fetching all tables from database with ID: {database_id}...")
        response = request_response("database/tables/database/{database_id}/")
        return self.handle_api_response(response) or []

    def get_all_data_from_database(self, database_id):
        self.print_verbose_message("[INFO] Fetching all data from database with ID: {database_id}...")
        tables = self.get_all_tables_from_database(database_id)
        data = {}

        for table in tables:
            table_id = table['id']
            table_name = table['name']
            data[table_name] = self.get_all_rows_from_table(table_id)

        return data

    def fetch_fields_for_table(self, table_id):
        """Fetch fields for a given table."""
        response = requests.get(f"{self.base_url}database/fields/table/{table_id}/", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to fetch fields for table {table_id}. Status code: {response.status_code}")

    def merge_tables_on_reference(self, tables_data):
        self.print_verbose_message("Merging tables based on references...")
        indexed_data = self.index_tables_by_id(tables_data)
        link_fields = self.get_link_fields_for_all_tables(tables_data)
        self.embed_referenced_data_into_tables(tables_data, indexed_data, link_fields)
        self.print_verbose_message("Merged Tables Data:", tables_data)
        return tables_data

    def index_tables_by_id(self, tables_data):
        indexed_data = {table_name: {row['id']: row for row in rows} for table_name, rows in tables_data.items()}
        self.print_verbose_message("Indexed Data: {indexed_data}")
        return indexed_data

    def get_link_fields_for_all_tables(self, tables_data):
        link_fields = {}
        for table_name in tables_data:
            link_fields_for_table = self.get_link_fields_for_table(table_name)
            link_fields[table_name] = link_fields_for_table
            self.print_verbose_message("Link Fields For Table: {link_fields_for_table}")
        self.print_verbose_message("Link Fields: {link_fields}")
        return link_fields

    def get_link_fields_for_table(self, table_name):
        fields = self.fetch_fields_for_table(table_name)
        return [field for field in fields if field['type'] == 'link_row']

    def embed_referenced_data_into_tables(self, tables_data, indexed_data, link_fields):
        for table_name, rows in tables_data.items():
            for row in rows:
                self.embed_data_for_row(row, table_name, indexed_data, link_fields)

    def embed_data_for_row(self, row, table_name, indexed_data, link_fields):
        for link_field in link_fields[table_name]:
            field_name = link_field['name']
            referenced_table_id = link_field['link_row_table_id']
            if field_name in row and row[field_name] in indexed_data[referenced_table_id]:
                self.print_verbose_message(f"Embedding referenced data for field {field_name} in table {table_name}")
                row[field_name] = indexed_data[referenced_table_id][row[field_name]]
