import requests

class APIClient:
    """Simulates an external API Client."""
    def get_user_data(self, user_id):
        response = requests.get(f"https://api.example.com/users/{user_id}")
        if response.status_code == 200:
            return response.json()
        raise ValueError("API request failed")
    
class UserService:
    """Uses APIClient to fetch user data and process it."""
    def __init__(self, api_client):
        self.api_client = api_client

    def get_username(self, user_id):
        """Fetches a user and returns their username in uppercase."""
        user_data = self.api_client.get_user_data(user_id)
        return user_data["name"].upper()
    