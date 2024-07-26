from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

class DutyFormParser:
    '''
    Parses responses from the duty form

    Attributes:

    Methods:
    '''

    def __init__(self, forms_link: str = '') -> None:
        load_dotenv()
        self.sheets = self.authenticate_sheets()
        self.forms_link = forms_link

    def authenticate_sheets(self):
        return build('sheets', 'v4', developerKey=os.getenv('API_KEY')).spreadsheets()