import os
import pandas as pd


class DataManager:
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