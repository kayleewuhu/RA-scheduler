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
- You will need the questions and responses from a Google form that was filled out by every single person on the staff regarding their availabilities. You can get the responses in sheet form by clicking "View in Sheets" in the form responses. Here are the questions to be asked in the form (notes are in bolded and italicized and are not to be included in the actual form):
  - Preferred name ***(how the individual's name will appear in the final schedule)***  
    ![image](https://github.com/user-attachments/assets/71d2c09d-cef2-4c0e-9a67-8cac6e3700da)
  - Move in date? ***(when the individual moves in, so the scheduler does not schedule any shifts before that date...ensure this is in date format)***  
    ![image](https://github.com/user-attachments/assets/6e5b1da1-2692-4d07-88b9-5f5e2d956d2d)
  - Returning RA or new RA? ***(brand new RAs will not be scheduled for the first 2 weeks in order to account for their training)***  
    ![image](https://github.com/user-attachments/assets/83ba15d6-4ed1-4f9c-b1ba-b7707f22d712)
  - Have you been an RA in this community previously? ***(RAs that are new to this community will not be scheduled for the first week to account for training)***
    ![image](https://github.com/user-attachments/assets/74a7213a-31e5-4346-b959-d6a034dc9abc)
  - What dates can you NOT be on duty? (MM-DD FORMAT) ***(You can have the question validate the responses by this regular expression: ^((0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])(,\s*(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))*)$ )***
    ![image](https://github.com/user-attachments/assets/e2a63f55-11f5-4763-827c-cad5fd4f9745)
  - What days of the week can you NOT be on duty? ***(Perhaps make this a multiple choice question)***
    ![image](https://github.com/user-attachments/assets/9d912329-5497-4c76-9b01-e2ea62eef2f4)
  - Frontload or backload? ***(Whether the individual would like to have more shifts early on, or later on)***
    ![image](https://github.com/user-attachments/assets/ed446881-bec4-4b08-ae15-57743be1dd21)

### Running the program
- In the console, run `python main.py`.
- The program will ask the following questions that you must answer and press enter after each (again notes are bolded and italicized):
  - What is the first day of duty (yyyy-mm-dd)? ***(This will be the first date of the schedule)***
  - What is the last day of duty (yyyy-mm-dd)? ***(This will be the last date of the schedule)***
  - List all the dates that are holidays (yyyy-mm-dd): ***(The shift of the previous day will have another point added to its worth, as the shift will be extended due to
    the holiday)***
  - Provide the date range for break (yyyy-mm-dd to yyyy-mm-dd): ***(The schedule will cover either Thanksgiving or Spring break, so include the date range of that break.
    Include the weekends of that break)***
  - List the names (as they appear in the form responses) of the RAs on half staff: ***(These are the people that will be in the building over the break, so these are
    the only people that may be on duty during the break)***
  - Please enter the url to the form containing the responses: ***(This is the URL to the Google Spreadsheet that has all the form responses. The sheet does not have to be publicly accessible)***
  - What would you like to title the schedule? ***(This will be the title of the Google Spreadsheet schedule)***
- Finally, the program will pop up a window in your browser asking you to login to a Google account. Ensure this account has access to the URL that you just gave the program containg all the form responses. This part of the program utilizes Google OAuth 2.0.
- Once you login, the program will create a spreadsheet with your account, titled what you specified, containing the entire duty schedule. Below is a sample:
  - The first sheet will be the schedule. 
  ![image](https://github.com/user-attachments/assets/ff799e10-6520-425a-a66e-825a0fd01b53)
  - The second sheet will be the total points assigned to every individual.
  ![image](https://github.com/user-attachments/assets/1d3adbaa-2456-425c-8b59-72ca6f6cad6e)



      
