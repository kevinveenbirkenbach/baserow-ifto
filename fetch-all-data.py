import requests
import argparse

def create_headers(api_key):
    """Create headers for API requests."""
    return {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

def handle_api_response(response):
    """Handle API response, check for errors and decode JSON."""
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} from Baserow API.")
        print("Response content:", response.content.decode())
        return None

    try:
        return response.json()
    except requests.RequestsJSONDecodeError:
        print("Error: Failed to decode the response as JSON.")
        return None

def get_all_rows_from_table(base_url, api_key, table_id):
    headers = create_headers(api_key)
    rows = []
    next_url = f"{base_url}database/rows/table/{table_id}/"

    while next_url:
        response = requests.get(next_url, headers=headers)
        data = handle_api_response(response)
        if not data:
            break
        rows.extend(data['results'])
        next_url = data['next']

    return rows

def get_all_tables_from_database(base_url, api_key, database_id):
    headers = create_headers(api_key)
    response = requests.get(f"{base_url}database/tables/database/{database_id}/", headers=headers)
    return handle_api_response(response) or []

def get_all_data_from_database(base_url, api_key, database_id):
    tables = get_all_tables_from_database(base_url, api_key, database_id)
    data = {}

    for table in tables:
        table_id = table['id']
        table_name = table['name']
        data[table_name] = get_all_rows_from_table(base_url, api_key, table_id)

    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch all data from a Baserow database.")
    parser.add_argument("base_url", help="Base URL of your Baserow instance, e.g., https://YOUR_BASEROW_INSTANCE_URL/api/")
    parser.add_argument("api_key", help="Your Baserow API key.")
    parser.add_argument("database_id", help="ID of the Baserow database you want to fetch data from.")
    
    args = parser.parse_args()

    all_data = get_all_data_from_database(args.base_url, args.api_key, args.database_id)
    print(all_data)
