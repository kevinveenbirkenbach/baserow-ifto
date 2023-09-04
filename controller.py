import argparse
import json
from baserow_api import BaserowAPI
import view

def handle_output(quiet,data):
    if not quiet:
        view.print_json_output(data)

def main():
    args = parse_arguments()
    api = BaserowAPI(args.base_url, args.api_key, args.verbose)
    
    if args.table_ids:
        tables_data = fetch_table_data(api, args.table_ids)
        if "linked_fields" in args.output:
            linked_fields_data = api.get_link_fields_for_all_tables(tables_data)
            handle_output(args.quiet, linked_fields_data)
            
        if "matrix" in args.output:
            merged_data = api.merge_tables_on_reference(tables_data)
            handle_output(args.quiet, merged_data)
                
        if "tables" in args.output:
            handle_output(args.quiet, tables_data)
    
    if args.database_id:
        all_data = api.get_all_data_from_database(args.database_id)
        if not args.quiet:
            view.print_json_output(all_data)
        
def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch all data from a Baserow database.")
    parser.add_argument("base_url", help="Base URL of your Baserow instance, e.g., https://YOUR_BASEROW_INSTANCE_URL/api/")
    parser.add_argument("api_key", help="Your Baserow API key.")
    parser.add_argument("--database_id", help="ID of the Baserow database you want to fetch data from.", default=None)
    parser.add_argument("--table_ids", help="IDs of the Baserow tables you want to fetch data from, separated by commas.", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode for debugging.")
    parser.add_argument("--output", choices=["linked_fields", "tables", "matrix"], default=[], nargs='+', help="Specify the type(s) of output: linked_fields, matrix, content or both")
    parser.add_argument("--quiet", action="store_true", help="Suppress output of json")
    return parser.parse_args()

def fetch_table_data(api, table_ids_str):
    table_ids = table_ids_str.split(',')
    tables_data = {}
    for table_id in table_ids:
        table_data = api.get_all_rows_from_table(table_id.strip())
        tables_data[table_id] = table_data
    return tables_data

if __name__ == "__main__":
    main()
