import requests
import argparse
import json

def create_headers(api_key):
    """Create headers for API requests."""
    return {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

def handle_api_response(response, verbose):
    """Handle API response, check for errors and decode JSON."""
    if verbose:
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

def get_all_rows_from_table(base_url, api_key, table_id, verbose):
    if verbose:
        print(f"[INFO] Fetching all rows from table with ID: {table_id}...")
    headers = create_headers(api_key)
    rows = []
    next_url = f"{base_url}database/rows/table/{table_id}/"

    while next_url:
        response = requests.get(next_url, headers=headers)
        if verbose:
            print("Headers:", headers)
            print("Requesting:", next_url)
        data = handle_api_response(response, verbose)
        if not data:
            break
        rows.extend(data['results'])
        next_url = data['next']

    return rows

def get_all_tables_from_database(base_url, api_key, database_id, verbose):
    if verbose:
        print(f"[INFO] Fetching all tables from database with ID: {database_id}...")
    headers = create_headers(api_key)
    response = requests.get(f"{base_url}database/tables/database/{database_id}/", headers=headers)
    if verbose:
        print("Headers:", headers)
    return handle_api_response(response, verbose) or []

def get_all_data_from_database(base_url, api_key, database_id, verbose):
    if verbose:
        print(f"[INFO] Fetching all data from database with ID: {database_id}...")
    tables = get_all_tables_from_database(base_url, api_key, database_id, verbose)
    data = {}

    for table in tables:
        table_id = table['id']
        table_name = table['name']
        data[table_name] = get_all_rows_from_table(base_url, api_key, table_id, verbose)

    return data

def fetch_fields_for_table(base_url, api_key, table_id):
    """Fetch fields for a given table."""
    headers = create_headers(api_key)
    response = requests.get(f"{base_url}database/fields/table/{table_id}/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch fields for table {table_id}. Status code: {response.status_code}")

def merge_tables_on_reference(base_url, api_key, tables_data,verbose):
    if verbose:
        print(
            "Merge tables based on references.\n"
            "Assumes that a reference from one table to another is represented by a field in the dictionary\n"
            "that has the same name as the referenced table and contains the ID of the referenced row.\n"
        ) 
    # Create a mapping of table names to their rows indexed by ID
    indexed_data = {table_name: {row['id']: row for row in rows} for table_name, rows in tables_data.items()}

    # Fetch field information for each table and identify link fields
    link_fields = {}
    for table_name in tables_data:
        fields = fetch_fields_for_table(base_url, api_key,table_name)
        link_fields[table_name] = [field for field in fields if field['type'] == 'link_row']

    # Embed referenced data into tables
    for table_name, rows in tables_data.items():
        for row in rows:
            for link_field in link_fields[table_name]:
                field_name = link_field['name']
                referenced_table_id = link_field['link_row_table_id']
                if field_name in row and row[field_name] in indexed_data[referenced_table_id]:
                    if verbose: print("Embed the referenced row data under the reference field")
                    row[field_name] = indexed_data[referenced_table_id][row[field_name]]
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

    if not args.database_id and not args.table_ids:
        print("Error: Either database_id or table_ids must be provided.")
        exit(1)

    if args.table_ids:
        table_ids = args.table_ids.split(',')
        tables_data = {}
        for table_id in table_ids:
            table_data = get_all_rows_from_table(args.base_url, args.api_key, table_id.strip(), args.verbose)
            tables_data[table_id] = table_data

        if args.matrix:
            merged_data = merge_tables_on_reference(args.base_url, args.api_key,tables_data, args.verbose)
            if not args.quiet: print(json.dumps(merged_data, indent=4))
        else:
            if not args.quiet: print(json.dumps(tables_data, indent=4))
    else:
        all_data = get_all_data_from_database(args.base_url, args.api_key, args.database_id, args.verbose)
        if not args.quiet: print(json.dumps(all_data, indent=4))