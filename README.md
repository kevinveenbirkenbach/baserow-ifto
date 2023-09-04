# Baserow IFTO API Wrapper

This repository contains a Python-based API wrapper for Baserow, designed to provide Input, Filter, Transform, and Output (IFTO) functionalities for Baserow data.

## Features

- Fetch all rows from a specific table in Baserow.
- Fetch all tables from a specific database in Baserow.
- Fetch all data from a specific database in Baserow.
- Handle API responses, including error checking and JSON decoding.
- Merge tables based on references.
- Command-line interface for fetching data.

## Getting Started

### Prerequisites

- Python 3.x
- `requests` library. Install it using:
  ```bash
  pip install requests
  ```

### Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/baserow-ifto.git
   cd baserow-ifto
   ```

2. Use the script with the required arguments:
   ```bash
   python controller.py BASE_URL API_KEY --database_id DATABASE_ID
   ```

   Replace `BASE_URL`, `API_KEY`, and `DATABASE_ID` with the appropriate values:

   - `BASE_URL`: Base URL of your Baserow instance, e.g., `https://YOUR_BASEROW_INSTANCE_URL/api/`
   - `API_KEY`: Your Baserow API key.
   - `DATABASE_ID`: ID of the Baserow database you want to fetch data from.

   The script will fetch all the data from the specified Baserow database and print it to the console.

### Additional Options

- `--table_ids`: Specify IDs of the Baserow tables you want to fetch data from, separated by commas.
- `--matrix`: Merge tables based on references.
- `-v` or `--verbose`: Enable verbose mode for debugging.
- `--linked_fields`: Outputs the linked tables.
- `--quiet`: Suppress output of JSON.

## License

All rights to this code belong in equal parts to [Marco Petersen](mailto:m@rcopetersen.com) and [Kevin Veen-Birkenbach](mailto:kevin@veen.world).

## Contributing

If you have suggestions, improvements, or any issues, feel free to open an issue or submit a pull request. Your contributions are always welcome!