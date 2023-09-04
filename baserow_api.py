import requests
import json

class BaserowAPI:
    def __init__(self, base_url, api_key, verbose=False):
        self.base_url = base_url
        self.api_key = api_key
        self.verbose = verbose
        self.headers = self.create_headers()
        self.print_verbose_message(f"Headers:{self.headers}")

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
        self.print_verbose_message(f"Response Status Code: {response.status_code}")
        self.print_verbose_message(f"Response Headers: {response.headers}")
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from Baserow API.")
            response_content=response.content.decode()
            print("Response content: {response_content}")
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
        next_url = f"database/rows/table/{table_id}/"

        while next_url:
            response=self.request_response(next_url)
            self.print_verbose_message(f"Requesting: {next_url}")
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
        response = self.request_response(f"database/tables/database/{database_id}/")
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
        self.print_verbose_message("Fetch fields for a given table.")
        response = self.request_response(f"database/fields/table/{table_id}/")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to fetch fields for table {table_id}. Status code: {response.status_code}")
        

    def get_link_fields_for_all_tables(self, tables_data):
        link_fields = {}
        for table_name in tables_data:
            link_fields_for_table = self.get_link_fields_for_table(table_name)
            link_fields[table_name] = link_fields_for_table
        return link_fields

    def get_link_fields_for_table(self, table_name):
        fields = self.fetch_fields_for_table(table_name)
        return [field for field in fields if field['type'] == 'link_row']

    def get_tables(self,table_ids):
        tables_data = {}
        for table_id in table_ids:
            table_data = self.get_all_rows_from_table(table_id.strip())
            tables_data[table_id] = table_data
        return tables_data

    def build_matrix(self, tables_data, reference_map={}):
        """Build a matrix with linked rows filled recursively."""
        reference_map_child = reference_map.copy()

        for table_name, table_rows in tables_data.copy().items():
            self.process_link_fields(table_name, tables_data, reference_map_child)
            self.fill_cells_with_related_content(table_name, table_rows, reference_map_child)

        return tables_data

    def fill_cells_with_related_content(self, table_name, table_rows, reference_map_child):
        """Fill cells with related content."""
        for table_row in table_rows:
            self.print_verbose_message(f"table_row: {table_row}")
            """Check if the iteration should be skipped based on conditions."""
            for table_column_name, table_cell_content in table_row.items():
                if table_column_name in reference_map_child:
                    cell_identifier = self.generate_cell_identifier(table_name, table_column_name, table_row)
                    embeder_field_id = reference_map_child[table_column_name]["link_row_related_field_id"]

                    self.print_verbose_message(f"cell_identifier: {cell_identifier}")
                    self.print_verbose_message(f"embeder_field_id: {embeder_field_id}")

                    if cell_identifier in reference_map_child[table_column_name]["embeded"]:
                        self.print_verbose_message(f"NOT EMBEDED!")
    
    def generate_embeded_cell_identifier(self, table_id, table_column_id, table_row_id):
        return self.generate_cell_identifier(table_id, "field_" + str(table_column_name_id), table_row_id);

    def generate_cell_identifier(self, table_name, table_column_name, table_row):
        """Generate cell identifier."""
        return "table_" + table_name + "_" + table_column_name + "_row_" + str(table_row["id"])

    def process_link_fields(self, table_name, tables_data, reference_map_child):
        """Process link fields for a given table."""
        link_fields = self.get_link_fields_for_table(table_name)

        for link_field in link_fields:
            self.load_table_data_if_not_present(link_field, tables_data)
            self.update_reference_map(link_field, reference_map_child)

    def load_table_data_if_not_present(self, link_field, tables_data):
        """Load table data if it's not already loaded."""
        link_row_table_id = link_field["link_row_table_id"]

        if link_row_table_id not in tables_data:
            tables_data[link_row_table_id] = self.get_all_rows_from_table(link_row_table_id)

    def update_reference_map(self, link_field, reference_map_child):
        """Update the reference map with the link field data."""
        link_field_name = "field_" + str(link_field["id"])

        if link_field_name not in reference_map_child:
            reference_map_child[link_field_name] = link_field
            reference_map_child[link_field_name]["embeded"] = []
 
       

