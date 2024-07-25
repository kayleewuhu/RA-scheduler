from datetime import date, timedelta
from constants import DaysOfWeek, Distribution

class RaAvailability:
    '''
    Represents a single RA and their availabilities and preferences

    Attributes:

    Methods:
    '''

    def __init__(self, name: str = "", no_dates: list[date] = [],
                 no_days: list[DaysOfWeek] = [],
                 distribution: Distribution = 0,
                 returner: bool = False,
                 community_returner: bool = False) -> None:
        '''
        Initializes attributes

        Parameters:
          name - name of RA
          no_dates - dates that RA cannot be on duty
          no_days - days of the week that RA cannot be on duty
          pref_no_days - days of the week that RA prefers not be on duty
          pref_days - days of the week that RA prefers be on duty
          distribution - whether RA prefers to frontload or backload (or none)
          pref_no_ppl - people RA prefers not be on duty with
          pref_ppl - people RA prefers be on duty with

        '''
        self.name = name
        self.no_dates = no_dates
        self.no_days = no_days
        # self.pref_no_days = pref_no_days
        # self.pref_days = pref_days
        self.distribution = distribution
        self.returner = returner
        self.community_returner = community_returner


class Ra:
    '''
    Represents an RA 
    '''

    def __init__(self, 
                 name: str = '', 
                 points: int = 0, 
                 half_staff: bool = False, 
                 returner: bool = True,
                 community_returner: bool = True) -> None:
        self.name = name
        self.pts = points
        self.half_staff = half_staff
        self.returner = returner
        self.community_returner = community_returner 


class Holidays:
    '''
    Represents a holiday
    '''
    def __init__(self, double_len: list[date] = [], breaks: list[date] = [], hard_shifts: list[date] = []) -> None:
        self.double_len = double_len
        self.breaks = breaks
        self.hard_shifts = hard_shifts
        self.half_staff_pt = False
    
    def add_previous_day(self) -> None:
        first_day = self.breaks[0]
        prev_day = first_day - timedelta(days=1)
        self.breaks.insert(0, prev_day)
