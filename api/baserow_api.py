import requests
import json

class BaserowAPI:
    def __init__(self, base_url, api_key, verbose=False):
        self.base_url = base_url
        self.api_key = api_key
        self.verbose = verbose
        self.headers = self.create_headers()

    def create_headers(self):
        """Create headers for API requests."""
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

    def request_response(self, command):
        return requests.get(f"{self.base_url}{command}", headers=self.headers)

    def handle_api_response(self, response):
        """Handle API response, check for errors and decode JSON."""
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from Baserow API.")
            response_content = response.content.decode()
            print("Response content: {response_content}")
            return None

        try:
            return response.json()
        except:
            print({response.content})
            print("Error: Failed to decode the response as JSON.")
            return None