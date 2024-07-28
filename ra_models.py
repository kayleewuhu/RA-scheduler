from datetime import date, timedelta
from constants import DaysOfWeek, Distribution


class RaAvailability:
    '''
    Represents a single RA and their availabilities and preferences

    Attributes:

    Methods:
    '''

    def __init__(self, name: str = "", move_in_date: date = None,
                 no_dates: list[date] = [],
                 no_days: list[DaysOfWeek] = [],
                 distribution: Distribution = Distribution.NONE,
                 returner: bool = False,
                 community_returner: bool = False) -> None:
        '''
        Initializes attributes

        Parameters:
          name - name of RA
          move_in_date - date the RA is moving in 
          no_dates - dates that RA cannot be on duty
          no_days - days of the week that RA cannot be on duty
          distribution - whether RA prefers to frontload or backload (or none)
          returner - if the RA has been an RA before
          community_returner - if the RA has been an RA in this community before
        '''
        self.name = name
        self.move_in_date = move_in_date
        self.no_dates = no_dates
        self.no_days = no_days
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
        '''
        Initializes attributes

        Parameters:
          name - name of RA
          points - how many points the RA has in duty shifts
          half_staff - if the RA is on half staff or not
          returner - if the RA has been an RA before
          community_returner - if the RA has been an RA in this community before
        '''
        self.name = name
        self.pts = points
        self.half_staff = half_staff
        self.returner = returner
        self.community_returner = community_returner 


class Holidays:
    '''
    Represents a holiday
    '''
    def __init__(self, double_len: list[date] = [], breaks: list[date] = []) -> None:
        '''
        Initialize attributes

        Parameters:
            double_len: List of dates (usually holidays) that are double the normal shift length for that day
            breaks: List of dates on a break
        '''
        self.double_len = double_len
        self.breaks = breaks
    
    def add_previous_day(self) -> None:
        first_day = self.breaks[0]
        prev_day = first_day - timedelta(days=1)
        self.breaks.insert(0, prev_day)
