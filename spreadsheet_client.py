import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from ra_models import RaAvailability
from datetime import datetime, date
from constants import DaysOfWeek, Distribution

# Define the scope for Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class SpreadsheetClient:
    '''
    Parses responses from the duty form

    Attributes:

    Methods:
    '''

    def __init__(self, start_date: date) -> None:
        '''
        Initialize attributes

        Parameters:
            start_date - first day of duty (yyyy-mm-dd)
        '''
        self.year = start_date.year

    def authenticate_user(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        return creds

    def create_sheet_resource(self, cred):
        return build('sheets', 'v4', credentials=cred).spreadsheets()

    def extract_spreadsheet_id(self, sheet_url):
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid URL")

    def get_form_answers(self, sheet_resource, sheet_url: str):
        sheet_id = self.extract_spreadsheet_id(sheet_url)
        response = sheet_resource.values().get(spreadsheetId=sheet_id, range='Form responses 1').execute()
        form_answers = response.get('values', [])
        return form_answers
    
    def match_column_property(self, title_columns: list[str]):
        availability_properties = {}
        for idx, col in enumerate(title_columns):
            col = col.lower()
            if 'preferred name' in col:
                availability_properties['name'] = idx
            elif all(word in col for word in ['move in', 'date']):
                availability_properties['move_in_date'] = idx
            elif all(word in col for word in ['dates', 'not', 'duty']):
                availability_properties['no_dates'] = idx
            elif all(word in col for word in ['days', 'not', 'duty']):
                availability_properties['no_days'] = idx
            elif any(word in col for word in ['frontload', 'backload', 'distribution']):
                availability_properties['distribution'] = idx
            elif all(word in col for word in ['returning', 'ra']):
                availability_properties['returner'] = idx
            elif all(word in col for word in ['been', 'community', 'previously']):
                availability_properties['community_returner'] = idx
            else:
                continue
        return availability_properties
    
    def construct_availabilities(self, form_answers):
        title_row = form_answers.pop(0)
        property_indices = self.match_column_property(title_row)
        ra_availabilities = []

        for row in form_answers:
            ra_properties = {}
            for property, idx in property_indices.items():
                response = row[idx]
                formatted_response = response
                if not response:
                    continue
                if property == 'move_in_date':
                    date_object = datetime.strptime(response, '%m/%d/%Y')
                    formatted_response = date_object.date()
                elif property == 'no_dates':
                    date_strings = map(lambda date: date.strip(), response.split(','))
                    formatted_response = [datetime.strptime(f'{self.year}-{month_day}', '%Y-%m-%d').date() for month_day in date_strings]
                elif property == 'no_days':
                    days = response.split(', ')
                    formatted_response = []
                    for day in days:
                        formatted_response.append(DaysOfWeek[day.upper()])
                elif property == 'distribution':
                    if response == 'Frontload':
                        formatted_response = Distribution.FRONTLOAD
                    elif response == 'Backload':
                        formatted_response = Distribution.BACKLOAD
                    else:
                        formatted_response == Distribution.NONE
                elif property == 'returner':
                    formatted_response = (response == 'Returner')
                elif property == 'community_returner':
                    formatted_response = (response == 'Yes')
                # else:
                #     raise ValueError('Unsupported property')
                ra_properties[property] = formatted_response
            ra = RaAvailability(**ra_properties)
            ra_availabilities.append(ra)
            ra.print_all()
        return ra_availabilities
                
    # def authenticate_user(self):
    #     creds = None
    #     token_path = 'token.pickle'
    #     credentials_path = 'credentials.json'

    # # Load existing credentials from a file if available
    #     if os.path.exists(token_path):
    #         with open(token_path, 'rb') as token:
    #             creds = pickle.load(token)

    # # If there are no valid credentials available, prompt the user to log in
    #     if not creds or not creds.valid:
    #         if creds and creds.expired and creds.refresh_token:
    #             creds.refresh(Request())
    #         else:
    #             flow = InstalledAppFlow.from_client_secrets_file(
    #                 credentials_path, SCOPES)
    #             creds = flow.run_local_server(port=0)

    #     # Save the credentials for the next run
    #     with open(token_path, 'wb') as token:
    #         pickle.dump(creds, token)
    #     return creds

    def create_sheet(self, creds):
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets().create(body={
            'properties': {'title': 'New Schedule'}
        }).execute()
        return sheet
