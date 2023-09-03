import requests
import argparse
import json

class BaserowAPI:
    def __init__(self, base_url, api_key, verbose=False):
        self.base_url = base_url
        self.api_key = api_key
        self.verbose = verbose

    def create_headers(self):
        """Create headers for API requests."""
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

    def handle_api_response(self, response):
        """Handle API response, check for errors and decode JSON."""
        if self.verbose:
            print("[INFO] Handling API response...")
            print("Response Status Code:", response.status_code)
            print("Response Headers:", response.headers)
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
        headers = self.create_headers()
        rows = []
        next_url = f"{self.base_url}database/rows/table/{table_id}/"

        while next_url:
            response = requests.get(next_url, headers=headers)
            if self.verbose:
                print("Headers:", headers)
                print("Requesting:", next_url)
            data = self.handle_api_response(response)
            if not data:
                break
            rows.extend(data['results'])
            next_url = data['next']

        return rows

    def get_all_tables_from_database(self, database_id):
        if self.verbose:
            print(f"[INFO] Fetching all tables from database with ID: {database_id}...")
        headers = self.create_headers()
        response = requests.get(f"{self.base_url}database/tables/database/{database_id}/", headers=headers)
        if self.verbose:
            print("Headers:", headers)
        return self.handle_api_response(response) or []

    def get_all_data_from_database(self, database_id):
        if self.verbose:
            print(f"[INFO] Fetching all data from database with ID: {database_id}...")
        tables = self.get_all_tables_from_database(database_id)
        data = {}

        for table in tables:
            table_id = table['id']
            table_name = table['name']
            data[table_name] = self.get_all_rows_from_table(table_id)

        return data

    def fetch_fields_for_table(self, table_id):
        """Fetch fields for a given table."""
        headers = self.create_headers()
        response = requests.get(f"{self.base_url}database/fields/table/{table_id}/", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch fields for table {table_id}. Status code: {response.status_code}")

    def merge_tables_on_reference(self, tables_data):
        if self.verbose:
            print("Merging tables based on references...")

        # Create a mapping of table names to their rows indexed by ID
        indexed_data = {table_name: {row['id']: row for row in rows} for table_name, rows in tables_data.items()}
        if self.verbose:
            print("Indexed Data:", indexed_data)

        # Fetch field information for each table and identify link fields
        link_fields = {}
        for table_name in tables_data:
            fields = self.fetch_fields_for_table(table_name)
            link_fields_for_table = [field for field in fields if field['type'] == 'link_row']
            link_fields[table_name] = link_fields_for_table
        if self.verbose:
            print("Link Fields:", link_fields)
            print("Link Fields For Table:", link_fields_for_table)

        # Embed referenced data into tables
        for table_name, rows in tables_data.items():
            for row in rows:
                for link_field in link_fields[table_name]:
                    field_name = link_field['name']
                    referenced_table_id = link_field['link_row_table_id']
                    if field_name in row and row[field_name] in indexed_data[referenced_table_id]:
                        if self.verbose:
                            print(f"Embedding referenced data for field {field_name} in table {table_name}")
                        row[field_name] = indexed_data[referenced_table_id][row[field_name]]

        if self.verbose:
            print("Merged Tables Data:", tables_data)
        return tables_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch all data from a Baserow database.")
    parser.add_argument("base_url", help="Base URL of your Baserow instance, e.g., https://YOUR_BASEROW_INSTANCE_URL/api/")
    parser.add_argument("api_key", help="Your Baserow API key.")
    parser.add_argument("--database_id", help="ID of the Baserow database you want to fetch data from.", default=None)
    parser.add_argument("--table_ids", help="IDs of the Baserow tables you want to fetch data from, separated by commas.", default=None)
    parser.add_argument("--matrix", action="store_true", help="Merge tables based on references.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode for debugging.")
    parser.add_argument("--quiet", action="store_true", help="Suppress output of json")

    args = parser.parse_args()
    api = BaserowAPI(args.base_url, args.api_key, args.verbose)

    if not args.database_id and not args.table_ids:
        print("Error: Either database_id or table_ids must be provided.")
        exit(1)

    if args.table_ids:
        table_ids = args.table_ids.split(',')
        tables_data = {}
        for table_id in table_ids:
            table_data = api.get_all_rows_from_table(table_id.strip())
            tables_data[table_id] = table_data

        if args.matrix:
            merged_data = api.merge_tables_on_reference(tables_data)
            if not args.quiet: print(json.dumps(merged_data, indent=4))
        else:
            if not args.quiet: print(json.dumps(tables_data, indent=4))
    else:
        all_data = api.get_all_data_from_database(args.database_id)
        if not args.quiet: print(json.dumps(all_data, indent=4))
