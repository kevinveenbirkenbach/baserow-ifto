# baserow-ifto

This repository contains the Input Filter Transform and Output (IFTO) scripts to work with Baserow data.

## Usage

### Fetching All Data from a Baserow Database

We have a Python script that allows you to fetch all data from a Baserow database using its API. 

#### Requirements

- Python 3.x
- `requests` library. You can install it using pip:

```bash
pip install requests
```

#### How to Use

1. Clone this repository:

```bash
git clone https://github.com/yourusername/baserow-ifto.git
cd baserow-ifto
```

2. Run the script with the required arguments:

```bash
python fetch-all-data.py BASE_URL API_KEY DATABASE_ID
```

Replace `BASE_URL`, `API_KEY`, `DATABASE_ID` with the appropriate values:

- `BASE_URL`: Base URL of your Baserow instance, e.g., `https://YOUR_BASEROW_INSTANCE_URL/api/`
- `API_KEY`: Your Baserow API key.
- `DATABASE_ID`: ID of the Baserow database you want to fetch data from.

The script will then fetch all the data from the specified Baserow database and print it to the console.

## Contributing

If you have suggestions or improvements, feel free to open an issue or submit a pull request. Your contributions are welcome!
