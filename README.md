# Resident Assistant Duty Scheduler
This repository houses a command line program that creates a schedule for Resident Assistant (RA) duty shifts. It assumes that there are a constant given number of people on duty per day. 
The program will read responses from a Google Spreadsheet, which should contain the responses of all RAs regarding their availabilities during the semester and then 
create a new Google Spreadsheet that displays who is on which shifts, abiding by those availabilities.

### Files
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

### How to run the program

      
