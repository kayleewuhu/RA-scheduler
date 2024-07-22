from datetime import datetime, date, timedelta
from typing import List
from ra_models import DaysOfWeek, Holidays
from ortools.sat.python import cp_model
from day import Day
from constants import DAYS_OF_WEEK, Semester
from ra_models import RaAvailability, Ra


class DutyScheduler:
    '''
    Creates a duty schedule

    Attributes:

    Methods:
    '''

    def __init__(self, start_date: str, end_date: str, ra_availabilities: List[RaAvailability],
                 holidays: Holidays = None) -> None:
        '''
        Initializes attributes

        Parameters:
          start_date - first day of duty (yyyy-mm-dd)
          end_date - last day of duty (yyyy-mm-dd)
          ra_availabilities - all the responses from the RAs that indicate their availabilities & preferences
        '''
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        self.semester_type = self.determine_semester_season()
        self.ra_availabilities = ra_availabilities

        day_dict_pts = self.create_day_dict()
        self.day_dict = day_dict_pts[0]
        self.total_pts = day_dict_pts[1]
        # self.half_staff =
        self.holidays = holidays

    def determine_semester_season(self) -> Semester:
        '''
        Determines which semester the schedule is being made for

        Parameters: None

        Returns
          the semester type for this schedule
        '''
        start_month = self.start_date.month
        if start_month == 1:
            return Semester.SPRING
        elif start_month == 8:
            return Semester.FALL
        elif start_month == 5:
            return Semester.SUMMER
        else:
            raise ValueError("Semester type cannot be determined")

    def create_day_dict(self) -> tuple[dict[date, Day], int]:
        '''
        Creates a dictionary of information for every single day from start_date to end_date 
        and calculates total points, excluding special cases or holidays

        Parameters: None

        Returns:
          a dictionary of info about all days in schedule, and the total number of points in the schedule
          dictionary: key -> date, value -> day object
        '''
        num_days = (self.end_date - self.start_date).days + 1
        cur_date = self.start_date
        day_idx = self.start_date.weekday()
        days = {}
        total_pts = 0

        for _ in range(num_days):
            cur_day = Day(cur_date, DAYS_OF_WEEK[day_idx])
            days[cur_date] = cur_day
            total_pts += cur_day.pts * cur_day.ppl
            cur_date = cur_date + timedelta(days=1)
            day_idx = (day_idx + 1) % 7

        return days, total_pts

    # def revise_total_pts(self) -> None:
    #     '''
    #     Handles special case day points (holidays) and
    #     evens out the total number of points so that all RAs can have an equal amount of points

    #     Parameters: None

    #     Returns: None
    #     '''
    #     # handles all mandatory holidays that make previous day 24 hour shift
    #     for holiday in self.holidays.double_len:
    #         prev_shift = self.day_dict[holiday - timedelta(days=1)]
    #         prev_shift.add_pts(1)
    #         self.total_pts += prev_shift.ppl

    #     # handles breaks (including the surrounding weekends)
    #     for holiday in self.holidays.breaks:
    #         # Thanksgiving
    #         if self.semester_type == Semester.FALL:
    #             shift = self.day_dict[holiday]
    #         elif self.semester_type == Semester.SPRING:
    #             shift

    #     while (self.total_pts) % len(self.ra_availabilities) != 0:

        # def total_weekdays(self) -> int:
        #     '''
        #     Calculate total weekdays for the time period

        #     Parameters: None

        #     Returns:
        #       total number of weekdays
        #     '''
        #     new_end = self.end_date + timedelta(days=1)
        #     new_end_date = new_end.strftime('%Y-%m-%d')
        #     # may want to incorporate excluding custom holidays, or can just do that in separate function
        #     total_weekdays = numpy.busday_count(self.start_date.strftime(
        #         '%Y-%m-%d'), new_end_date, weekmask='Sun Mon Tue Wed Thu')
        #     return total_weekdays

        # def weekday_shifts(self) -> int:
        #     '''
        #     Calculates total number of weekday shifts

        #     Parameters: None

        #     Returns:
        #       total number of weekday shifts
        #     '''
        #     weekdays = self.total_weekdays()
        #     return weekdays * self.people_per_shift_weekday

        # def total_weekends(self) -> int:
        #     '''
        #     Calculate total weekend days for the time period

        #     Parameters: None

        #     Returns:
        #       total number of weekend days
        #     '''
        #     new_end = self.end_date + timedelta(days=1)
        #     new_end_date = new_end.strftime('%Y-%m-%d')
        #     # may want to incorporate excluding custom holidays, or can just do that in separate function
        #     total_weekends = numpy.busday_count(self.start_date.strftime(
        #         '%Y-%m-%d'), new_end_date, weekmask='Fri Sat')
        #     return total_weekends

        # def weekend_shifts(self) -> int:
        #     '''
        #     Calculates total number of weekend shifts

        #     Parameters: None

        #     Returns:
        #       total number of weekend shifts
        #     '''
        #     weekends = self.total_weekends()
        #     return weekends * self.people_per_shift_weekend

    # def first_date_of_day(self, day: DaysOfWeek) -> date:
    #     '''
    #     Returns the date of the first occurrence of the given day of the week in the timeframe

    #     Parameters:
    #       day - day of the week

    #     Returns:
    #       the date of the first occurrence of the day
    #     '''
    #     start_day_idx = self.start_date.weekday()
    #     first_day_occurrence_idx = DAYS_OF_WEEK.index(day)
    #     num_days_btwn = abs(first_day_occurrence_idx - start_day_idx)
    #     if (start_day_idx > first_day_occurrence_idx):
    #         num_days_btwn = len(DAYS_OF_WEEK) - num_days_btwn
    #     first_day_date = self.start_date + timedelta(days=num_days_btwn)

    #     return first_day_date

    # def calculate_dates_of_day(self, day: DaysOfWeek) -> List[date]:
    #     '''
    #     Returns all dates that fall on the given day of the week within the timeframe

    #     Parameters:
    #       day - the day of the week

    #     Returns:
    #       list of dates
    #     '''
    #     day_date = self.first_date_of_day(day)
    #     all_day_dates = []

    #     while day_date <= self.end_date:
    #         all_day_dates.append(day_date)
    #         day_date = day_date + timedelta(days=7)

    #     return all_day_dates

    # def all_dates_of_all_days(self) -> dict:
    #     '''
    #     Returns a dictionary with all the dates each day of the week falls on

    #     Parameters: None

    #     Returns:
    #       dictionary containing all the dates for each day 
    #     '''
    #     all_days = {}
    #     for day_name in DAYS_OF_WEEK:
    #         all_dates = self.calculate_dates_of_day(day_name)
    #         all_days[day_name] = all_dates
    #     return all_days

    def no_days_for_all_ras(self, ras: List[Ra]) -> dict[DaysOfWeek, List[Ra]]:
        '''
        Creates a dict that assigns every day of the week with a list of RAs that cannot work that day

        Parameters:
          ras - a list of RA objects 

        Returns:
          a dictionary that with all the RAs that cannot work each day of the week
        '''
        no_days_for_ras = {DaysOfWeek.MONDAY: [], DaysOfWeek.TUESDAY: [], DaysOfWeek.WEDNESDAY: [],
                           DaysOfWeek.THURSDAY: [], DaysOfWeek.FRIDAY: [], DaysOfWeek.SATURDAY: [],
                           DaysOfWeek.SUNDAY: []}
        for ra, availability in zip(ras, self.ra_availabilities):
            for day in availability.no_days:
                no_days_for_ras[day].append(ra)
        return no_days_for_ras

    def create_ras(self) -> List[Ra]:
        '''
        Creates a list of RA objects from RA Availability objects

        Parameters: None

        Returns: 
          a list of RA objects that correspond with the RA availabilities
          (the availabilities are what is INPUT into the program, the list of RA objects will be the OUTPUT)
        '''
        ras = []
        for person in self.ra_availabilities:
            ras.append(Ra(person.name))
        return ras

    def create_or_model(self) -> None:
        '''
        Creates the OR model, adding constraints, and solving the problem
        '''
        # define variables
        staff_size = len(self.ra_availabilities)
        all_ras = self.create_ras()
        all_days = self.day_dict.values()

        model = cp_model.CpModel()

        # creating boolean variables (the assignments)
        assignments = {}
        for availability in all_ras:
            for day in all_days:
                for shift in range(day.ppl):
                    assignments[(availability, day, shift)] = model.new_bool_var(
                        (f"assignment_ra{availability}_date{day}_shift{shift}"))

        # adding constraints
        # exactly 1 RA per shift
        for day in all_days:
            for shift in range(day.ppl):
                model.add_exactly_one(
                    assignments[(ra, day, shift)] for ra in all_ras)

        # at most 1 shift per day for an RA
        for availability in all_ras:
            for day in all_days:
                model.add_at_most_one(
                    assignments[(availability, day, shift)] for shift in range(day.ppl))

        # calculate max and min total pts per RA
        min_pts_per_ra = self.total_pts // staff_size
        if self.total_pts % staff_size == 0:
            max_pts_per_ra = min_pts_per_ra
        else:
            max_pts_per_ra = min_pts_per_ra + 1

        # enforce max and min points per RA
        for availability in all_ras:
            pts_earned = []

            for day in all_days:
                for shift in range(day.ppl):
                    pts_earned.append(
                        assignments[(availability, day, shift)] * day.pts)
            model.add(min_pts_per_ra <= sum(pts_earned))
            model.add(sum(pts_earned) <= max_pts_per_ra)
        # print(min_shifts_per_ra)
        # print(max_shifts_per_ra)

        # dates that cannot be done
        for availability, ra in zip(self.ra_availabilities, all_ras):
            for date in availability.no_dates:
                day = self.day_dict[date]
                for shift in range(day.ppl):
                    if day in all_days:
                        model.add(assignments[(ra, day, shift)] == 0)

        no_days_dict = self.no_days_for_all_ras(all_ras)
        # days of the week that cannot be done
        for day in all_days:
            day_of_week = day.day_of_week
            for ra in no_days_dict[day_of_week]:
                for shift in range(day.ppl):
                    model.add(assignments[(ra, day, shift)] == 0)

        solver = cp_model.CpSolver()
        status = solver.solve(model)
        print(status)
    # Print solution.
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print('Solution found')
        # Print solution details if needed
            for d in all_days:
              print(f"Date: {d.date}, Day: {d.day_of_week}")
              for e in all_ras:
                  for s in range(d.ppl):
                    if solver.Value(assignments[e, d, s]):
                        e.pts += d.pts
                        print(f"  RA {e.name} works shift {s}")
            
            for e in all_ras:
                print(f"RA {e.name} has {e.pts} pts")
        else:
            print('No solution found')
