import requests

BASE_URL = "https://YOUR_BASEROW_INSTANCE_URL/api/"
API_KEY = "YOUR_API_KEY"
HEADERS = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json"
}

def get_all_rows_from_table(table_id):
    rows = []
    next_url = f"{BASE_URL}database/rows/table/{table_id}/"

    while next_url:
        response = requests.get(next_url, headers=HEADERS)
        data = response.json()
        rows.extend(data['results'])
        next_url = data['next']

    return rows

def get_all_tables_from_database(database_id):
    response = requests.get(f"{BASE_URL}database/tables/database/{database_id}/", headers=HEADERS)
    tables = response.json()
    return tables

def get_all_data_from_database(database_id):
    tables = get_all_tables_from_database(database_id)
    data = {}

    for table in tables:
        table_id = table['id']
        table_name = table['name']
        data[table_name] = get_all_rows_from_table(table_id)

    return data

database_id = "YOUR_DATABASE_ID"
all_data = get_all_data_from_database(database_id)
print(all_data)
