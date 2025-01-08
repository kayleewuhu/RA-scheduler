# Resident Assistant Duty Scheduler
This repository houses a command line program that creates a schedule for Resident Assistant (RA) duty shifts. It assumes that there are a constant given number of people on duty per day. 
The program will read responses from a Google Spreadsheet, which should contain the responses of all RAs regarding their availabilities during the semester and then 
create a new Google Spreadsheet that displays who is on which shifts, abiding by those availabilities.

## Files
- constants.py: contains the constants and enums utilized in the program
  - in the last line of the file, there is a CONSTANTS value initialized as follows: Constants(_, _)
  - the first value represents the number of people on shift on weekdays (Sunday-Thursday nights)
  - the second value represents the number of people on shift on weekends (Friday, Saturday nights)
- duty_scheduler.py: contains logic regarding the creation of the schedule
  - class DutyScheduler: creates the duty schedule using Google's or-tools library and constraint programming
  - will return values
- main.py: entrance point of the program
  - asks for user input and validates input
- ra_models.py: contains classes regarding information about an RA
  - class RaAvailability: an object that contains the information regarding a single RA's availability preferences
  - class Ra: an object that represents an RA
  - class Holidays: an object that contains the holiday/break shift dates (special shifts that are worth more points than usual)
- schedule_models.py:
  - class Day: an object that contains information about the shift on a specific day (date, day of week, number of people on the shift, number of points the shift is worth)
  - class ScheduleDay: an object that represents the duty shift of a specific day (Day, who is on duty)
- spreadsheet_client.py: contains all logic regarding Google SpreadSheet manipulation
  - class SpreadsheetClient: contains logic for reading, creating, and editing Google Spreadsheets (uses Google's Spreadsheet API)

## How to run the program
### Requirements before running
- You must have python3 installed.
- You will also need to install google or-tools by running the command
  `pip install or-tools`
- You will also need a `credentials.json` file with Google Oauth 2.0 client credentials. This is required as the program uses Google Spreadsheets API and needs the user
  to authenticate and login to their google account. You can get these credentials by going to the Google API Console and creating your own.
- You will need the questions and responses from a Google form that was filled out by every single person on the staff regarding their availabilities. Here are the questions to be asked in the form (notes are in bolded and italicized and are not to be included in the actual form):
  - Preferred name ***(how the individual's name will appear in the final schedule)***  
    ![image](https://github.com/user-attachments/assets/71d2c09d-cef2-4c0e-9a67-8cac6e3700da)
  - Move in date? ***(when the individual moves in, so the scheduler does not schedule any shifts before that date...ensure this is in date format)***  
    ![image](https://github.com/user-attachments/assets/6e5b1da1-2692-4d07-88b9-5f5e2d956d2d)
  - Returning RA or new RA? ***(brand new RAs will not be scheduled for the first 2 weeks in order to account for their training)***
  - Have you been an RA in this community previously? ***(RAs that are new to this community will not be scheduled for the first week to account for training)***
  - What dates can you NOT be on duty? (MM-DD FORMAT) ***(You can have the question validate the responses by this regular expression: ^((0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])(,\s*(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))*)$ )***
  - What days of the week can you NOT be on duty? ***(Perhaps make this a multiple choice question)***
  - Frontload or backload? ***(Whether the individual would like to have more shifts early on, or later on)***


### Running the program
- In the console, run `python main.py`.


      
