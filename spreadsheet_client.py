import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from ra_models import RaAvailability, Ra
from schedule_models import ScheduleDay
from datetime import datetime, date
from constants import DaysOfWeek, Distribution, CONSTANTS

# Define the scope for Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class SpreadsheetClient:
    '''
    Parses responses from the duty form

    Attributes:

    Methods:
    '''

    def __init__(self, start_date: date, schedule_name: str) -> None:
        '''
        Initialize attributes

        Parameters:
            start_date - first day of duty
        '''
        self.year = start_date.year
        self.name = schedule_name if schedule_name else 'New Schedule'
        creds = self.authenticate_user()
        self.sheet = self.create_sheet_resource(creds)
        # self.scheduler = scheduler

    def authenticate_user(self):
        '''
        Gets session token for spreadsheet API authentication

        Parameters: None

        Returns:
            OAuth credentials
        '''
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        return creds

    def create_sheet_resource(self, cred):
        '''
        Creates sheet resource

        Parameters:
            cred - OAuth credentials
        Returns:
            sheet resource
        '''
        return build('sheets', 'v4', credentials=cred).spreadsheets()

    def extract_spreadsheet_id(self, sheet_url: str) -> str:
        '''
        Extracts spreadsheet id from the url

        Parameters:
            sheet_url - the url of the spreadsheet to be parsed

        Returns:
            the id of the spreadsheet
        '''
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
        if match:
            return match.group(1)
        else:
            raise ValueError('Invalid URL')

    def get_form_answers(self, sheet_url: str) -> list[list[str]]:
        '''
        Returns the content of the given spreadsheet

        Parameters:
            sheet_url - the spreadsheet url

        Returns:
            the content of the spreadsheet as a list of lists
        '''
        sheet_id = self.extract_spreadsheet_id(sheet_url)
        response = self.sheet.values().get(
            spreadsheetId=sheet_id, range='Form responses 1').execute()
        form_answers = response.get('values', [])
        return form_answers

    def match_column_property(self, title_columns: list[str]) -> dict[str, int]:
        '''
        Finds the column index for each attribute of the RA availability class

        Parameters:
            title_columns - the first row of the spreadsheet that has all the names of the columns

        Returns:
            a dict matching every RA availability attribute with its column index
        '''
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

    def construct_availabilities(self, form_answers: list[str]) -> list[RaAvailability]:
        '''
        Constructs the list of RA availability objects from all the spreadsheet responses

        Parameters:
            form_answers - the form responses from the spreadsheet (without the first title row)

        Returns:
            list of RA availabilities
        '''
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
                    date_strings = map(
                        lambda date: date.strip(), response.split(','))
                    formatted_response = [datetime.strptime(
                        f'{self.year}-{month_day}', '%Y-%m-%d').date() for month_day in date_strings]
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

    def create_sheet(self) -> str:
        '''
        Creates a new spreadsheet

        Parameters: None
        Returns:
            the spreadsheet id
        '''
        spreadsheet = self.sheet.create(body={
            'properties': {'title': self.name},
            'sheets': [
                {
                    'properties': {
                        'title': 'Duty',
                    }
                }
            ]
        }, fields='spreadsheetId').execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')

        # Fetch the spreadsheet metadata to get the sheet ID
        spreadsheet_metadata = self.sheet.get(
            spreadsheetId=spreadsheet_id).execute()

        # Find the sheet ID of the first sheet
        sheet_id = spreadsheet_metadata['sheets'][0]['properties']['sheetId']
        return spreadsheet_id, sheet_id

    def base_schedule(self, spreadsheet_id: str, sheet_id: str, schedule: list[ScheduleDay], ras: list[Ra], days_per_month: dict) -> str:
        start_row = 1
        requests = []

        for month, length in days_per_month.items():
            requests += [
                {
                    'mergeCells': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': start_row,
                            'endRowIndex': start_row + length,
                            'startColumnIndex': 0,
                            'endColumnIndex': 1
                        },
                        'mergeType': 'MERGE_ALL'
                    }
                },
                {
                    'updateCells': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': start_row,
                            'endRowIndex': start_row + length,
                            'startColumnIndex': 0,
                            'endColumnIndex': 1
                        },
                        'rows': [
                            {
                                'values': [
                                    {
                                        'userEnteredFormat': {
                                            'textFormat': {
                                                'fontSize': 50,
                                                'bold': True
                                            },
                                            'textRotation': {
                                                'angle': 90
                                            },
                                            'horizontalAlignment': 'CENTER',
                                            'verticalAlignment': 'MIDDLE'
                                        },
                                        'userEnteredValue': {'stringValue': month}
                                    }
                                ]
                            }
                        ],
                        'fields': 'userEnteredValue,userEnteredFormat(textFormat,textRotation,horizontalAlignment,verticalAlignment)'
                    }
                }
            ]
            start_row += length

        max_ras_per_shift = max(
            CONSTANTS.PPL_PER_SHIFT_WEEKDAY, CONSTANTS.PPL_PER_SHIFT_WEEKEND)
        requests += [
            {
                'mergeCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 1,
                        'endColumnIndex': 3
                    },
                    'mergeType': 'MERGE_ALL'
                }
            },
            {
                'updateCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 1,
                        'endColumnIndex': 3
                    },
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredFormat': {
                                        'textFormat': {
                                            'fontSize': 10,
                                            'bold': True
                                        },
                                        'horizontalAlignment': 'CENTER',
                                        'verticalAlignment': 'MIDDLE'
                                    },
                                    'userEnteredValue': {'stringValue': 'DAY'}

                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue,userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)'
                }
            },
            {
                'updateCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 3,
                        'endColumnIndex': 4
                    },
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredFormat': {
                                        'textFormat': {
                                            'fontSize': 10,
                                            'bold': True
                                        },
                                        'horizontalAlignment': 'CENTER',
                                        'verticalAlignment': 'MIDDLE'
                                    },
                                    'userEnteredValue': {'stringValue': 'Points'}
                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue,userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)'
                }
            },
            {
                'updateCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 4,
                        'endColumnIndex': 5
                    },
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredFormat': {
                                        'textFormat': {
                                            'fontSize': 10,
                                            'bold': True
                                        },
                                        'horizontalAlignment': 'CENTER',
                                        'verticalAlignment': 'MIDDLE'
                                    },
                                    'userEnteredValue': {'stringValue': 'Notes'}
                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue,userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)'
                }
            },
            {
                'mergeCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 5,
                        'endColumnIndex': 5 + max_ras_per_shift
                    },
                    'mergeType': 'MERGE_ALL'
                }
            },
            {
                'updateCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 5,
                        'endColumnIndex': 5 + max_ras_per_shift
                    },
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredFormat': {
                                        'textFormat': {
                                            'fontSize': 10,
                                            'bold': True
                                        },
                                        'horizontalAlignment': 'CENTER',
                                        'verticalAlignment': 'MIDDLE'
                                    },
                                    'userEnteredValue': {'stringValue': 'RAs on Duty'}
                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue,userEnteredFormat(textFormat,horizontalAlignment,verticalAlignment)'
                }
            }
        ]

        response = self.sheet.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
