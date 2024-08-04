import sys
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
        'List all the days in which a 12 hour shift becomes a 24 hour shift (holidays, yyyy-mm-dd):\n', validate_holidays)
    extended_holiday = handle_input(
        'Provide the date range for break (yyyy-mm-dd to yyyy-mm-dd):\n', validate_break)
    half_staff = input(
        'List the names (as they appear in the form responses) of the RAs on half staff:\n')
    form_responses_url = input(
        'Please enter the url to the form containing the responses:\n')
    schedule_name = input('What is the title of the schedule?')

    spreadsheet_parser = SpreadsheetClient(start_date, schedule_name)
    creds = spreadsheet_parser.authenticate_user()
    sheet = spreadsheet_parser.create_sheet_resource(creds)
    form_answers = spreadsheet_parser.get_form_answers(
        sheet, form_responses_url)
    ra_availabilities = spreadsheet_parser.construct_availabilities(
        form_answers)

    holidays_object = Holidays(
        holidays if holidays else [], extended_holiday if extended_holiday else [])

    scheduler = DutyScheduler(start_date, end_date, ra_availabilities,
                              holidays_object, half_staff if half_staff else [])
    scheduler.create_or_model()


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
    # user_input()
    ras = [RaAvailability('Kari', date(2023, 12, 19), [date(2024, 1, 13), date(2024, 1, 14)], [DaysOfWeek.WEDNESDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Radhika', date(2024, 1, 2), [date(2024, 1, 3), date(2024, 1, 4)], [
                          DaysOfWeek.MONDAY, DaysOfWeek.FRIDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Annie', date(
               2024, 1, 2), distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Elise', date(
               2024, 1, 1), distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Luke', date(
               2024, 1, 2), distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Megan', date(2024, 1, 2), [date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6), date(2024, 3, 7), date(
               2024, 3, 8), date(2024, 3, 9), date(2024, 3, 10)], [DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Casey', date(2024, 1, 2), [date(2024, 1, 8), date(2024, 1, 17), date(2024, 2, 25), date(2024, 3, 20), date(2024, 3, 1), date(2024, 3, 2), date(2024, 3, 3), date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6), date(2024, 3, 7), date(2024, 3, 8), date(2024, 3, 9), date(2024, 3, 10), date(2024, 4, 1), date(2024, 4, 5)],
                          [DaysOfWeek.WEDNESDAY, DaysOfWeek.THURSDAY], returner=True, community_returner=True),
           RaAvailability('Matt', date(2024, 1, 3), [date(2024, 1, 6), date(2024, 1, 7), date(
               2024, 2, 14), date(2024, 3, 26), date(2024, 3, 27)], [DaysOfWeek.TUESDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Grace', date(2024, 1, 3), [date(2024, 1, 6), date(
               2024, 1, 7), date(2024, 2, 14), date(2024, 3, 27)], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Tony', date(2024, 1, 2), [date(2024, 3, 10), date(2024, 3, 11), date(2024, 3, 12), date(2024, 3, 13), date(
               2024, 3, 14), date(2024, 3, 15), date(2024, 3, 16), date(2024, 3, 17), date(2024, 3, 18)], [DaysOfWeek.SATURDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Nico', date(
               2024, 1, 2), distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Tula', date(2024, 1, 2), [date(2024, 2, 17), date(2024, 2, 18), date(2024, 2, 19), date(2024, 2, 20), date(
               2024, 2, 21), date(2024, 2, 22), date(2024, 2, 23), date(2024, 2, 24), date(2024, 2, 25)], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Fortune', date(2024, 1, 2), no_days=[
                          DaysOfWeek.MONDAY, DaysOfWeek.TUESDAY, DaysOfWeek.WEDNESDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Selma', date(2024, 1, 2), [date(2024, 2, 17), date(2024, 2, 18), date(
               2024, 2, 19), date(2024, 2, 20)], [DaysOfWeek.MONDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Tom', date(2024, 1, 2), no_days=[DaysOfWeek.TUESDAY, DaysOfWeek.THURSDAY,
                          DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY, DaysOfWeek.SUNDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Kaylee', date(2024, 1, 3),
                          returner=True, community_returner=True),
           RaAvailability('Bella', date(2024, 1, 2), [date(2024, 2, 15), date(2024, 2, 16), date(2024, 2, 17), date(2024, 2, 18), date(2024, 2, 19), date(2024, 3, 29), date(2024, 3, 1), date(
               2024, 3, 2), date(2024, 3, 3), date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6), date(2024, 3, 7), date(2024, 3, 8), date(2024, 3, 9), date(2024, 3, 10),], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Julia', date(2024, 1, 2), [date(2024, 1, 12), date(
               2024, 3, 30), date(2024, 3, 31)], [DaysOfWeek.THURSDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Ethan', date(2024, 1, 2), [date(2024, 4, 14)], [
                          DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Garett', date(2024, 1, 2), [date(2024, 3, 12)], [
                          DaysOfWeek.MONDAY, DaysOfWeek.TUESDAY, DaysOfWeek.WEDNESDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('David', date(
               2024, 1, 2), distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Karena', date(
               2024, 1, 2), distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('Derquan', date(2024, 1, 2), [date(2024, 3, 29), date(2024, 3, 30), date(
               2024, 3, 31)], [DaysOfWeek.WEDNESDAY, DaysOfWeek.SATURDAY], returner=True, community_returner=True),
           RaAvailability('Elizabeth', date(2024, 1, 2), [date(2024, 1, 13), date(2024, 1, 14), date(2024, 1, 15), date(
               2024, 3, 17), date(2024, 3, 29), date(2024, 3, 30), date(2024, 3, 31)], [DaysOfWeek.THURSDAY], distribution=Distribution.FRONTLOAD, returner=True, community_returner=True),
           RaAvailability('McKayla', date(2024, 1, 2),
                          returner=True, community_returner=True),
           RaAvailability('Joshie', date(2024, 1, 2), returner=True, community_returner=True)]

    holidays = Holidays(
        [date(2024, 1, 15), date(2024, 2, 19), date(2024, 4, 15)], [date(2024, 3, 1), date(2024, 3, 2), date(2024, 3, 3), date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6), date(2024, 3, 7), date(2024, 3, 8), date(2024, 3, 9), date(2024, 3, 10)])
    half_staff = ['Joshie', 'Grace', 'Matt', 'Tula', 'Selma', 'Tom', 'Ethan', 'Derquan', 'McKayla', 'Elizabeth', 'Elda', 'Tony']
    test = DutyScheduler(date(2024, 1, 2), date(2024, 5, 6), ras, holidays, half_staff)
    schedule, ras = test.create_or_model()
    spreadsheet = SpreadsheetClient(date(2024, 1, 2), 'Test schedule 2024')
    spreadsheet_id, sheet_id = spreadsheet.create_sheet()
    spreadsheet.base_schedule(spreadsheet_id, sheet_id, test.days_per_month)
    spreadsheet.add_schedule(spreadsheet_id, sheet_id, schedule)

