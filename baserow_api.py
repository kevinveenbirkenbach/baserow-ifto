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
        reference_map_child=reference_map.copy()
        for table_name, table_rows in list(tables_data.items()):
            link_fields=self.get_link_fields_for_table(table_name)
            #create a copy of reference map, so that it is just used for this path
            
            for link_field in link_fields:
                link_row_table_id=link_field["link_row_table_id"]
                # Load table data if not loaded
                if not link_row_table_id in tables_data:
                    tables_data[link_row_table_id]=self.get_all_rows_from_table(link_row_table_id) 

                link_field_name="field_" + str(link_field["id"])
                if not link_field_name in reference_map_child:
                    reference_map_child[link_field_name]=link_field
                    reference_map_child[link_field_name]["embeded_by"]=[]
 
        self.print_verbose_message(f"reference_map_child: {reference_map_child}")
 
        for table_name, table_rows in list(tables_data.items()):    
            # Fill cells with related content
            for table_row in table_rows:
                self.print_verbose_message(f"table_row: {table_row}");
                for table_column_name, table_cell_content in table_row.items():
                    # Don't iterate twice over the same part
                    if table_column_name in reference_map_child:
                        cell_identifier="table_" + table_name + "_" + table_column_name + "_row_" + str(table_row["id"])
                        self.print_verbose_message(f"cell_identifier: {cell_identifier}");
                        embeder_field_name=reference_map_child[table_column_name]["link_row_related_field_id"]
                        self.print_verbose_message(f"embeder_field_name: {embeder_field_name}");
                        if cell_identifier in reference_map_child[embeder_field_name]["embeded_by"]:
                            self.print_verbose_message(f"NOT EMBEDED!");
                        break
                    
        return tables_data

