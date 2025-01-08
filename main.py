import sys
from constants import Constants
from duty_scheduler import DutyScheduler
from spreadsheet_client import SpreadsheetClient
from ra_models import Holidays, RaAvailability, DaysOfWeek, Distribution
from datetime import datetime, date, timedelta
from typing import Callable

def user_input():
    start_date = handle_input(
        'What is the first day of duty (yyyy-mm-dd)?\n', validate_date)
    end_date = handle_input(
        'What is the last day of duty (yyyy-mm-dd)?\n', validate_date)
    validate_start_end(start_date, end_date)

    holidays = handle_input(
        'List all the dates that are holidays (yyyy-mm-dd):\n', validate_holidays)
    extended_holiday = handle_input(
        'Provide the date range for break (yyyy-mm-dd to yyyy-mm-dd):\n', validate_break)
    half_staff = input(
        'List the names (as they appear in the form responses) of the RAs on half staff:\n')
    form_responses_url = input(
        'Please enter the url to the form containing the responses:\n')
    schedule_name = input('What would you like to title the schedule?\n')

    spreadsheet_parser = SpreadsheetClient(start_date, schedule_name)
    form_answers = spreadsheet_parser.get_form_answers(form_responses_url)
    ra_availabilities = spreadsheet_parser.construct_availabilities(
        form_answers)

    holidays_object = Holidays(
        holidays if holidays else [], extended_holiday if extended_holiday else [])

    scheduler = DutyScheduler(start_date, end_date, ra_availabilities,
                              holidays_object, half_staff if half_staff else [])
    schedule, ras = scheduler.create_or_model()

    spreadsheet_id, sheet_ids = spreadsheet_parser.create_sheet()
    spreadsheet_parser.base_schedule(spreadsheet_id, sheet_ids[0], scheduler.days_per_month)
    response, cols = spreadsheet_parser.add_schedule(spreadsheet_id, schedule)
    spreadsheet_parser.add_half_staff(spreadsheet_id, ras, cols)
    spreadsheet_parser.add_ra_points(spreadsheet_id, ras)
    spreadsheet_parser.format_sheet(spreadsheet_id, sheet_ids)


def handle_input(prompt: str, validate_function: Callable[[str], any]):
    '''
    Handles receiving and validating input

    Parameters:
      prompt - the prompt for the user input
      validate_function - the function that validates the user's input

    Returns:
      the attribute from the input
    '''
    response = input(prompt)
    while True:
        validated_response = validate_function(response)
        if validated_response is not None:
            return validated_response
        else:
            response = input(f'Incorrect format. Retry.\n{prompt}')


def validate_date(date: str):
    '''
    Validates the user input is a date

    Parameters:
      date - the user input

    Returns:
      the date provided by the user as a date object
    '''
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        return date
    except ValueError:
        return None


def validate_start_end(start_date: date, end_date: date):
    '''
    Ensures the end date provided comes after the start date

    Parameters:
      start_date - the start date
      end_date - the end date

    Returns: None
    '''
    if (start_date > end_date):
        print('Start date comes after end date. Retry.')
        sys.exit()


def validate_holidays(holidays: str):
    '''
    Validates the list of holiday dates provided

    Parameters:
      holidays - the user input

    Returns:
      the holidays provided by the user as a list of dates
    '''
    if not holidays:
        return holidays
    try:
        holidays = [holiday.strip() for holiday in holidays.split(',')]
        holidays = [datetime.strptime(holiday, '%Y-%m-%d').date()
                    for holiday in holidays]
        return holidays
    except:
        return None


def validate_break(extended_holiday: str):
    '''
    Validates the break range provided by the user

    Parameters:
      extended_holiday - the range of dates of the break provided by user

    Returns:
      a list of dates that represent the break
    '''
    if not extended_holiday:
        return extended_holiday
    try:
        date_range = extended_holiday.split(' to ')
        date_range = [datetime.strptime(date, '%Y-%m-%d').date()
                      for date in date_range]

        start = date_range[0]
        end = date_range[1]
        if start > end:
            return None

        break_days = []
        while start <= end:
            break_days.append(start)
            start += timedelta(days=1)
        return break_days
    except:
        return None


if __name__ == '__main__':
    user_input()
