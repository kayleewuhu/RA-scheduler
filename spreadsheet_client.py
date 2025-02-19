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

    def create_sheet(self) -> tuple[str, str]:
        '''
        Creates a new spreadsheet

        Parameters: None
        Returns:
            the spreadsheet id
            the sheet id
        '''
        spreadsheet = self.sheet.create(body={
            'properties': {'title': self.name},
            'sheets': [
                {
                    'properties': {
                        'title': 'Duty',
                    }
                },
                {
                    'properties': {
                        'title': 'Per RA'
                    }
                }
            ]
        }, fields='spreadsheetId').execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')

        # Fetch the spreadsheet metadata to get the sheet ID
        spreadsheet_metadata = self.sheet.get(
            spreadsheetId=spreadsheet_id).execute()

        # Find the sheet ID of the first sheet
        sheet_ids = [sheet['properties']['sheetId']
                     for sheet in spreadsheet_metadata['sheets']]
        return spreadsheet_id, sheet_ids

    def base_schedule(self, spreadsheet_id: str, sheet_id: str, days_per_month: dict) -> str:
        '''
        Creates the headings for the schedule

        Parameters: 
            spreadsheet_id - spreadsheet id
            sheet_id - sheet id
            days_per_month - how many days per month

        Returns: None
        '''

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
                'updateCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 1
                    },
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredValue': {'stringValue': 'Month'}

                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue'
                }
            },
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
                                    'userEnteredValue': {'stringValue': 'DAY'}
                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue'
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
                                    'userEnteredValue': {'stringValue': 'Points'}
                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue'
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
                                    'userEnteredValue': {'stringValue': 'Notes'}
                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue'
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
                                    'userEnteredValue': {'stringValue': 'RAs on Duty'}
                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue'
                }
            }
        ]

        response = self.sheet.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        return response

    def add_schedule(self, spreadsheet_id: str, schedule: list[ScheduleDay]):
        '''
        Add the schedule to the spreadsheet

        Parameters:
          spreadsheet_id - spreadsheet id
          schedule - the schedule information (day & ras on)
        '''
        data = [
            {'range': 'Duty!B2',
             'values': [
                 [
                     day_prop.day.day_of_week.value,
                     day_prop.day.date.strftime('%b %d'),
                     day_prop.day.pts,
                     '24 HRS' if day_prop.day.pts == 2 else ''
                 ] + [ra.name for ra in day_prop.ras_on]
                 for day_prop in schedule
             ]
             }
        ]

        num_columns = max([len(row) for row in data[0]['values']])
        response = self.sheet.values().batchUpdate(spreadsheetId=spreadsheet_id, body={
            'valueInputOption': 'USER_ENTERED', 'data': data}).execute()
        return response, num_columns

    def add_half_staff(self, spreadsheet_id: str, ras: list[Ra], num_columns: int):
        '''
        Adds a list of all RAs on half staff to duty sheet

        Parameters:
          spreadsheet_id - id of spreadsheet
          ras - list of RAs
          num_columns - number of columns that are full
        '''
        range_start = chr(ord('A') + num_columns + 2)
        values = [['Half Staff']]
        for ra in ras:
            if ra.half_staff:
                values.append([ra.name])

        data = {
            'values': values
        }

        self.sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=f'Duty!{range_start}1',
            valueInputOption='USER_ENTERED',
            body=data
        ).execute()

    def add_ra_points(self, spreadsheet_id: str, ras: list[Ra]):
        '''
        Adds a table to the spreadsheet that specifies how many 1, 2, and 3 pt shifts 
        and total pts (and shadow shifts, half staff) each RA has (on separate sheet)

        Parameters:
          spreadsheet_id - id of spreadsheet
          ras - list of RAs 
          num_columns - number of columns that are full
        '''
        start_col = 'A'
        start_row = 1
        range_start = f'Per RA!{start_col}{start_row}'
        pts_col = 'D'
        first_ra_col = 'F'
        schedule_sheet = 'Duty'
        max_ras_per_shift = max(
            CONSTANTS.PPL_PER_SHIFT_WEEKDAY, CONSTANTS.PPL_PER_SHIFT_WEEKEND)

        values = [['RA', '1 point', '2 point',
                   '3 point', 'Total points', 'Shadow shifts', 'Half staff']]
        for ra in ras:
            start_row += 1
            row = [ra.name]
            for pt_val in range(1, 4):
                pt_count_formula = f'=COUNTIFS({schedule_sheet}!{pts_col}:{pts_col}, {pt_val}, {schedule_sheet}!{first_ra_col}:{
                    first_ra_col}, {start_col}{start_row})'
                for shift_col in range(1, max_ras_per_shift):
                    next_ra_col = chr(
                        ord('A') + (ord(first_ra_col) - ord('A') + shift_col) % 26)
                    pt_count_formula += f' + COUNTIFS({schedule_sheet}!{pts_col}:{pts_col}, {pt_val}, {schedule_sheet}!{next_ra_col}:{
                        next_ra_col}, {start_col}{start_row})'
                row.append(pt_count_formula)
            total_pts_formula = f'=SUMIF({schedule_sheet}!{first_ra_col}:{first_ra_col}, {start_col}{
                start_row}, {schedule_sheet}!{pts_col}:{pts_col})'
            for shift_col in range(1, max_ras_per_shift):
                next_ra_col = chr(
                    ord('A') + (ord(first_ra_col) - ord('A') + shift_col) % 26)
                total_pts_formula += f' + SUMIF({schedule_sheet}!{next_ra_col}:{next_ra_col}, {start_col}{
                    start_row}, {schedule_sheet}!{pts_col}:{pts_col})'
            row.append(total_pts_formula)
            row.append('0' if (ra.returner and ra.community_returner) else '')
            row.append('Yes' if ra.half_staff else 'No')
            values.append(row)

        data = {
            'values': values
        }

        self.sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_start,
            valueInputOption='USER_ENTERED',
            body=data
        ).execute()

    def format_sheet(self, spreadsheet_id: str, sheet_id: str):
        '''
        Formats spreadsheet

        Parameters:
          spreadsheet_id - id of spreadsheet
          sheet_id - id of sheet
        '''
        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id[0],
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE"
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment, verticalAlignment)"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id[1],
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE"
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment, verticalAlignment)"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id[0],
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat)"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id[1],
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat)"
                }
            }
        ]

        response = self.sheet.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        return response
