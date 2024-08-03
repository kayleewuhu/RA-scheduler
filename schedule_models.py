from datetime import date
from ra_models import Ra
from constants import WEEKENDS, CONSTANTS, DaysOfWeek

class Day:
    '''
    Represents the information about duty on a specific day

    Attributes:

    Methods:
    '''

    def __init__(self, date: date, day_of_week: DaysOfWeek) -> None:
        '''
        Initializes attributes

        Parameters:
          date - the date
          day_of_week - which day of the week
          num_of_ppl - how many people are on this shift
          pts - how many points this shift is
        '''
        self.date = date
        self.day_of_week = day_of_week
        self.ppl = self.calculate_num_ppl_on()
        self.pts = self.calculate_pts()

    def calculate_num_ppl_on(self) -> int:
        '''
        Calculates the number of people on this shift

        Parameters: None

        Returns:
          number of people on this shift
        '''
        if self.day_of_week in WEEKENDS:
            return CONSTANTS.PPL_PER_SHIFT_WEEKEND
        else: 
            return CONSTANTS.PPL_PER_SHIFT_WEEKDAY
    
    def calculate_pts(self) -> int:
        '''
        Calculates the number of points on this shift (based on weekday vs weekend)

        Parameters: None

        Returns:
          number of points this shift is
        '''
        if self.day_of_week in WEEKENDS:
            return 2
        else:
            return 1
    
    def add_pts(self, pts: int) -> int:
        '''
        Adds points to the current amount of points for this shift

        Parameters: 
          pts - number of pts to add 

        Returns: 
          new points for this shift
        '''
        self.pts += pts

        return self.pts

class ScheduleDay:
    '''
    Represents the duty schedule for one day

    Attributes:

    Methods:
    '''

    def __init__(self, day: Day, ras_on: list[Ra] = []) -> None:
        '''
        Initializes attributes

        Parameters:
          day - information regarding the day
          ras_on - the RAs scheduled to be on duty for this day
        '''
        self.day = day
        self.ras_on = ras_on

    def add_ra(self, ra):
        self.ras_on.append(ra)