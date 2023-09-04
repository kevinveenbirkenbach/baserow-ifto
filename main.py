import argparse
import json

from baserow_api import BaserowAPI

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
