import datetime
import numpy

class DutyScheduler:
  '''
  Creates a duty schedule

  Attributes:

  Methods:
  '''

  def __init__(self, start_date: str, end_date: str, people_per_shift_weekday: int, people_per_shift_weekend: int) -> None:
    '''
    Initializes attributes

    Parameters:
      start_date - first day of duty (yyyy-mm-dd)
      end_date - last day of duty (yyyy-mm-dd)
      people_per_shift_weekday - how many people on shift on a weekday
      people_per_shift_weekend - how many people on shift on a weekend
    '''
    self.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    self.end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    self.people_per_shift_weekday = people_per_shift_weekday
    self.people_per_shift_weekend = people_per_shift_weekend

  def total_weekdays(self) -> int:
    '''
    Calculate total weekdays for the time period

    Parameters: None
    
    Returns:
      total number of weekdays
    '''
    new_end = self.end_date + datetime.timedelta(days=1)
    new_end_date = new_end.strftime('%Y-%m-%d')
    # may want to incorporate excluding custom holidays, or can just do that in separate function
    total_weekdays = numpy.busday_count(self.start_date.strftime('%Y-%m-%d'), new_end_date, weekmask = 'Sun Mon Tue Wed Thu')
    return total_weekdays

  def weekday_shifts(self) -> int:
    '''
    Calculates total number of weekday shifts

    Parameters: None

    Returns:
      total number of weekday shifts
    '''
    weekdays = self.total_weekdays()
    return weekdays * self.people_per_shift_weekday

  def total_weekends(self) -> int:
    '''
    Calculate total weekend days for the time period

    Parameters: None
    
    Returns:
      total number of weekend days
    '''
    new_end = self.end_date + datetime.timedelta(days=1)
    new_end_date = new_end.strftime('%Y-%m-%d')
    # may want to incorporate excluding custom holidays, or can just do that in separate function
    total_weekends = numpy.busday_count(self.start_date.strftime('%Y-%m-%d'), new_end_date, weekmask = 'Fri Sat')
    return total_weekends
  
  def weekend_shifts(self) -> int:
    '''
    Calculates total number of weekend shifts

    Parameters: None

    Returns:
      total number of weekend shifts
    '''
    weekends = self.total_weekends()
    return weekends * self.people_per_shift_weekend