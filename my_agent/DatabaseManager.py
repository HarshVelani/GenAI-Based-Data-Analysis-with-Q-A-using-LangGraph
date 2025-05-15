import requests
import os
from typing import List, Any
import pandas as pd


class DatabaseManager:
    def __init__(self):
        self.endpoint_url = os.getenv("DB_ENDPOINT_URL")

    def get_data(self, path: str) -> str:
        """Retrieve the database schema."""
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File {path} does not exist.")
            
            if path.endswith('.csv'):
                df = pd.read_csv(path)
                # print(f"Data: {df.columns}")
                return df
            
            elif path.endswith('.xlsx'):
                df = pd.read_excel(path)
                return df
            
        except Exception as e:
            raise Exception(f"Error fetching schema: {str(e)}")

    def execute_query(self, uuid: str, query: str) -> List[Any]:
        """Execute SQL query on the remote database and return results."""
        try:
            response = requests.post(
                f"{self.endpoint_url}/execute-query",
                json={"uuid": uuid, "query": query}
            )
            response.raise_for_status()
            return response.json()['results']
        except requests.RequestException as e:
            raise Exception(f"Error executing query: {str(e)}")