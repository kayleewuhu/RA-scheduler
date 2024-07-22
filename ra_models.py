from datetime import date
from typing import List
from constants import DaysOfWeek, Distribution

class RaAvailability:
    '''
    Represents a single RA and their availabilities and preferences

    Attributes:

    Methods:
    '''

    def __init__(self, name: str = "", no_dates: List[date] = [],
                 no_days: List[DaysOfWeek] = [],
                 pref_days: List[str] = [], distribution: Distribution = 0,
                 pref_no_ppl: List[str] = [], pref_ppl: List[str] = []) -> None:
        '''
        Initializes attributes

        Parameters:
          name - name of RA
          id - id of RA
          no_dates - dates that RA cannot be on duty
          no_days - days of the week that RA cannot be on duty
          pref_no_days - days of the week that RA prefers not be on duty
          pref_days - days of the week that RA prefers be on duty
          distribution - whether RA prefers to frontload or backload
          pref_no_ppl - people RA prefers not be on duty with
          pref_ppl - people RA prefers be on duty with

        '''
        self.name = name
        # self.id = id
        self.no_dates = no_dates
        self.no_days = no_days
        # self.pref_no_days = pref_no_days
        self.pref_days = pref_days
        self.distribution = distribution
        self.pref_no_ppl = pref_no_ppl
        self.pref_ppl = pref_ppl


class Ra:
    '''
    Represents an RA 
    '''

    def __init__(self, name: str = '', points: int = 0, half_staff: bool = False) -> None:
        self.name = name
        self.pts = points
        self.half_staff = half_staff


class Holidays:
    '''
    Represents a holiday
    '''
    def __init__(self, double_len: List[date], breaks: List[date], hard_shifts: List[date]) -> None:
        self.double_len = double_len
        self.breaks = breaks
        self.hard_shifts = hard_shifts
