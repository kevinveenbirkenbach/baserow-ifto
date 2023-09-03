import requests
import argparse

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch all data from a Baserow database.")
    parser.add_argument("base_url", help="Base URL of your Baserow instance, e.g., https://YOUR_BASEROW_INSTANCE_URL/api/")
    parser.add_argument("api_key", help="Your Baserow API key.")
    parser.add_argument("--database_id", help="ID of the Baserow database you want to fetch data from.", default=None)
    parser.add_argument("--table_id", help="ID of the Baserow table you want to fetch data from.", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode for debugging.")
    
    args = parser.parse_args()

    if not args.database_id and not args.table_id:
        print("Error: Either database_id or table_id must be provided.")
        exit(1)

    if args.table_id:
        table_data = get_all_rows_from_table(args.base_url, args.api_key, args.table_id, args.verbose)
        print(table_data)
    else:
        all_data = get_all_data_from_database(args.base_url, args.api_key, args.database_id, args.verbose)
        print(all_data)
