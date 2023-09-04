import json 

def print_error_message(message):
    print(f"Error: {message}")

def print_json_output(data):
    print(json.dumps(data, indent=4))

def print_verbose_message(message, data=None):
    print(message)
    if data:
        print(data)
