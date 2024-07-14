from datetime import datetime, date, timedelta
from typing import List
from kiwisolver import Solver
from matplotlib.dates import DAYS_PER_WEEK
import numpy
from ra_availabilities import DaysOfWeek
from ortools.sat.python import cp_model

from ra_availabilities import RaAvailability


class DutyScheduler:
    '''
    Creates a duty schedule

    Attributes:

    Methods:
    '''
    DAYS_OF_WEEK = [DaysOfWeek.MONDAY, DaysOfWeek.TUESDAY, DaysOfWeek.WEDNESDAY,
                    DaysOfWeek.THURSDAY, DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY,
                    DaysOfWeek.SUNDAY]

    def __init__(self, start_date: str, end_date: str, people_per_shift_weekday: int, people_per_shift_weekend: int, ra_availabilities: List[RaAvailability]) -> None:
        '''
        Initializes attributes

        Parameters:
          start_date - first day of duty (yyyy-mm-dd)
          end_date - last day of duty (yyyy-mm-dd)
          people_per_shift_weekday - how many people on shift on a weekday
          people_per_shift_weekend - how many people on shift on a weekend
        '''
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        self.people_per_shift_weekday = people_per_shift_weekday
        self.people_per_shift_weekend = people_per_shift_weekend
        self.ra_availabilities = ra_availabilities

    def total_weekdays(self) -> int:
        '''
        Calculate total weekdays for the time period

        Parameters: None

        Returns:
          total number of weekdays
        '''
        new_end = self.end_date + timedelta(days=1)
        new_end_date = new_end.strftime('%Y-%m-%d')
        # may want to incorporate excluding custom holidays, or can just do that in separate function
        total_weekdays = numpy.busday_count(self.start_date.strftime(
            '%Y-%m-%d'), new_end_date, weekmask='Sun Mon Tue Wed Thu')
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
        new_end = self.end_date + timedelta(days=1)
        new_end_date = new_end.strftime('%Y-%m-%d')
        # may want to incorporate excluding custom holidays, or can just do that in separate function
        total_weekends = numpy.busday_count(self.start_date.strftime(
            '%Y-%m-%d'), new_end_date, weekmask='Fri Sat')
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

    def first_date_of_day(self, day: DaysOfWeek) -> date:
        '''
        Returns the date of the first occurrence of the given day of the week in the timeframe

        Parameters:
          day - day of the week

        Returns:
          the date of the first occurrence of the day
        '''
        start_day_idx = self.start_date.weekday()
        first_day_occurrence_idx = DutyScheduler.DAYS_OF_WEEK.index(day)
        num_days_btwn = abs(first_day_occurrence_idx - start_day_idx)
        if (start_day_idx > first_day_occurrence_idx):
            num_days_btwn = len(DutyScheduler.DAYS_OF_WEEK) - num_days_btwn
        first_day_date = self.start_date + timedelta(days=num_days_btwn)

        return first_day_date

    def calculate_dates_of_day(self, day: DaysOfWeek) -> List[date]:
        '''
        Returns all dates that fall on the given day of the week within the timeframe

        Parameters:
          day - the day of the week

        Returns:
          list of dates
        '''
        day_date = self.first_date_of_day(day)
        all_day_dates = []

        while day_date <= self.end_date:
            all_day_dates.append(day_date)
            day_date = day_date + timedelta(days=7)

        return all_day_dates

    def all_dates_of_all_days(self) -> dict:
        '''
        Returns a dictionary with all the dates each day of the week falls on

        Parameters: None

        Returns:
          dictionary containing all the dates for each day 
        '''
        all_days = {}
        for day_name in DutyScheduler.DAYS_OF_WEEK:
            all_dates = self.calculate_dates_of_day(day_name)
            all_days[day_name] = all_dates
        return all_days

    def total_points(self) -> int:
        '''
        Calculates total number of points
          - weekdays are 1 point
          - weekends are 2 points
          - holidays are 3 points ( unhandled )

        Parameters: None

        Returns:
          total number of points
        '''
        weekday_points = self.weekday_shifts() * 1
        weekend_points = self.weekend_shifts() * 2
        return weekday_points + weekend_points

    def create_or_model(self) -> None:
        # define variables
        staff_size = len(self.ra_availabilities)
        all_ras = [ra.name for ra in self.ra_availabilities]
        shifts_per_day = 2
        all_shifts_per_day = range(shifts_per_day)
        # num_days = self.total_weekdays() + self.total_weekends()
        num_days = (self.end_date - self.start_date).days + 1
        # list of date objects from start date to end date (inclusive)
        all_days = [self.start_date +
                    timedelta(days=day) for day in range(num_days)]
        # for day in range(num_days):
        #     date = self.start_date + timedelta(days=day)
        #     all_days.append({"Date": date, "Day": DutyScheduler.DAYS_OF_WEEK[date.weekday()]})
        model = cp_model.CpModel()

        # creating boolean variables (the assignments)
        assignments = {}
        for ra in all_ras:
            for day in all_days:
                for shift in all_shifts_per_day:
                    assignments[(ra, day, shift)] = model.new_bool_var(
                        (f"assignment_ra{ra}_date{day}_shift{shift}"))

        # exactly 1 RA per shift
        for day in all_days:
            for shift in all_shifts_per_day:
                model.add_exactly_one(
                    assignments[(ra, day, shift)] for ra in all_ras)

        # at most 1 shift per day
        for ra in all_ras:
            for day in all_days:
                model.add_at_most_one(
                    assignments[(ra, day, shift)] for shift in all_shifts_per_day)

        # calculate max and min shifts per RA
        min_shifts_per_ra = (shifts_per_day * num_days) // staff_size
        if shifts_per_day * num_days % staff_size == 0:
            max_shifts_per_ra = min_shifts_per_ra
        else:
            max_shifts_per_ra = min_shifts_per_ra + 1

        # enforce max and min shifts per RA
        for ra in all_ras:
            shifts_worked = []
            for day in all_days:
                for shift in all_shifts_per_day:
                    shifts_worked.append(assignments[(ra, day, shift)])
            model.add(min_shifts_per_ra <= sum(shifts_worked))
            model.add(sum(shifts_worked) <= max_shifts_per_ra)
        # print(min_shifts_per_ra)
        # print(max_shifts_per_ra)

        # dates that cannot be done
        for ra in self.ra_availabilities:
            for date in ra.no_dates:
                for shift in all_shifts_per_day:
                    if date in all_days:
                        model.add(assignments[(ra.name, date, shift)] == 0)

        all_days_and_dates = self.all_dates_of_all_days()
        # days of the week that cannot be done
        for ra in self.ra_availabilities:
            for day in ra.no_days:
                dates_of_day = all_days_and_dates[day]
                for shift in all_shifts_per_day:
                    for date in dates_of_day:
                        if date in all_days:
                            model.add(assignments[(ra.name, date, shift)] == 0)

        # solve
        solver = cp_model.CpSolver()
        status = solver.solve(model)
        print(status)
    # Print solution.
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print('Solution found')
        # Print solution details if needed
            self.test_assignments(assignments, solver,
                                  all_days, all_ras, range(shifts_per_day), all_days_and_dates)
        else:
            print('No solution found')

    def test_assignments(self, assignments: dict, solver: cp_model.CpSolver, days: List[date], ras: List[str], shifts: List[int], days_dates: dict) -> None:
        for d in days:
            print(f"Date: {d}, Day: {d.strftime('%A')}")
            for e in ras:
                for s in shifts:
                    if solver.Value(assignments[e, d, s]):
                        print(f"  RA {e} works shift {s}")