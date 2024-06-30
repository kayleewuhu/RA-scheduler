class DutyScheduler:
  """
  Creates a duty schedule

  Attributes:

  Methods:
  """

  def __init__(self, start_date, end_date, people_per_shift_weekday, people_per_shift_weekend) -> None:
    """
    Initializes attributes

    Parameters:
      start_date - first day of duty
      end_date - last day of duty
      people_per_shift_weekday - how many people on shift on a weekday
      people_per_shift_weekend - how many people on shift on a weekend
    """
    self.start_date = start_date
    self.end_date = end_date
    self.people_per_shift_weekday = people_per_shift_weekday
    self.people_per_shift_weekend = people_per_shift_weekend