"""
Log data to a Google Sheet.

Format:
    - Created At
    - Reddit Post ID
    - Reddit Post Title
    - Reddit Post URL
    - Reddit Post Score
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime


class SheetsLogger:
    def __init__(self):
        self.client = gspread.authorize(
            Credentials.from_service_account_info(
                json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON")),
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
        )
        self.sheet = self.client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
        self.sheet = self.sheet.sheet1
    
    def get_ids_set(self):
        return set([row[1] for row in self.sheet.get_all_values()[1:]])
    
    def format_data(self, post_id: str, post_title: str, post_url: str, post_score: int):
        return [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            post_id,
            post_title,
            post_url,
            post_score,
        ]

    def append_row_from_dict(self, data: dict):
        self.sheet.append_row(self.format_data(**data))

    def append_row(self, post_id: str, post_title: str, post_url: str, post_score: int):
        self.sheet.append_row(self.format_data(post_id, post_title, post_url, post_score))

    
    






