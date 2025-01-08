from dataclasses import dataclass
from enum import Enum


class DaysOfWeek(Enum):
    MONDAY = 'Mon'
    TUESDAY = 'Tues'
    WEDNESDAY = 'Wed'
    THURSDAY = 'Thurs'
    FRIDAY = 'Fri'
    SATURDAY = 'Sat'
    SUNDAY = 'Sun'


DAYS_OF_WEEK = [DaysOfWeek.MONDAY, DaysOfWeek.TUESDAY, DaysOfWeek.WEDNESDAY,
                DaysOfWeek.THURSDAY, DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY,
                DaysOfWeek.SUNDAY]

WEEKENDS = [DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY]
WEEKDAYS = [DaysOfWeek.SUNDAY, DaysOfWeek.MONDAY, DaysOfWeek.TUESDAY, 
            DaysOfWeek.WEDNESDAY, DaysOfWeek.THURSDAY]


class Semester(Enum):
    FALL = 0
    SPRING = 1
    SUMMER = 2

class Distribution(Enum):
    FRONTLOAD = 0
    BACKLOAD = 1
    NONE = 2

@ dataclass(frozen=True)
class Constants:
    PPL_PER_SHIFT_WEEKDAY: int
    PPL_PER_SHIFT_WEEKEND: int

# Initialize the constant
# user_value = input('Enter a value for the constant: ')
CONSTANTS = Constants(2, 2)
