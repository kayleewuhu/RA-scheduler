from datetime import datetime, date, timedelta
from ra_models import DaysOfWeek, Holidays
from ortools.sat.python import cp_model
from schedule_models import Day, ScheduleDay
from constants import DAYS_OF_WEEK, Semester, WEEKENDS, Distribution
from ra_models import RaAvailability, Ra


class DutyScheduler:
    '''
    Creates a duty schedule

    Attributes:

    Methods:
    '''

    def __init__(self, start_date: date, end_date: date, ra_availabilities: list[RaAvailability],
                 holidays: Holidays = Holidays(), half_staff: list[str] = []) -> None:
        '''
        Initializes attributes

        Parameters:
          start_date - first day of duty 
          end_date - last day of duty 
          ra_availabilities - all the responses from the RAs that indicate their availabilities & preferences
        '''
        self.start_date = start_date
        self.end_date = end_date
        self.semester_type = self.determine_semester_season()
        self.ra_availabilities = ra_availabilities

        day_dict_pts = self.create_day_dict()
        self.day_dict = day_dict_pts[0]
        self.total_pts = day_dict_pts[1]
        self.days_per_month = day_dict_pts[2]
        self.half_staff = half_staff
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
            raise ValueError('Semester type cannot be determined')

    def create_day_dict(self) -> tuple[dict[date, Day], int]:
        '''
        Creates a dictionary of information for every single day from start_date to end_date
        and calculates total points, excluding special cases or holidays

        Parameters: None

        Returns:
          a dictionary of info about all days in schedule
          dictionary: key -> date, value -> day object
          the total number of points in the schedule
          a dictionary of how many days per month
        '''
        num_days = (self.end_date - self.start_date).days + 1
        cur_date = self.start_date
        day_idx = self.start_date.weekday()
        days = {}
        total_pts = 0
        months = {}

        for _ in range(num_days):
            cur_day = Day(cur_date, DAYS_OF_WEEK[day_idx])
            days[cur_date] = cur_day
            total_pts += cur_day.pts * cur_day.ppl

            month = cur_date.strftime('%B')
    
            if month in months:
                months[month] += 1
            else:
                months[month] = 1

            cur_date = cur_date + timedelta(days=1)
            day_idx = (day_idx + 1) % 7
        return days, total_pts, months

    def revise_total_pts(self) -> None:
        '''
        Handles special case day points (holidays) and
        evens out the total number of points so that all RAs can have an equal amount of points

        Parameters: None

        Returns: None
        '''
        # handles all mandatory holidays that make previous day 24 hour shift
        for holiday in self.holidays.double_len:
            prev_shift = self.day_dict[holiday - timedelta(days=1)]
            prev_shift.add_pts(1)
            self.total_pts += prev_shift.ppl

        # handles breaks (including the surrounding weekends)
        # Thanksgiving: assume the dates given are Wednesday - Sunday
        # add point to Tuesday before
        if self.semester_type == Semester.FALL:
            self.holidays.add_previous_day()
            for holiday in self.holidays.breaks:
                day = self.day_dict[holiday]
                if (day.day_of_week == DaysOfWeek.SUNDAY or
                    day.day_of_week == DaysOfWeek.TUESDAY or
                        day.day_of_week in WEEKENDS):
                    pt_increase = 1
                else:
                    pt_increase = 2
                day.add_pts(pt_increase)
                self.total_pts += pt_increase * day.ppl
        # Spring break: assume the dates given are Saturday - Sunday (1 week + 1 day)
        # add point to Friday before
        elif self.semester_type == Semester.SPRING:
            self.holidays.add_previous_day()
            for holiday in self.holidays.breaks:
                day = self.day_dict[holiday]
                day.add_pts(1)
                self.total_pts += day.ppl

    def no_days_for_all_ras(self, ras: list[Ra]) -> dict[DaysOfWeek, list[Ra]]:
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

    def create_ras(self) -> list[Ra]:
        '''
        Creates a list of RA objects from RA Availability objects

        Parameters: None

        Returns:
          a list of RA objects that correspond with the RA availabilities
          (the availabilities are what is INPUT into the program, the list of RA objects will be the OUTPUT)
        '''
        ras = []
        for person in self.ra_availabilities:
            if person.name in self.half_staff:
                half_staff = True
            else:
                half_staff = False
            ras.append(Ra(name=person.name, half_staff=half_staff,
                       returner=person.returner, community_returner=person.community_returner))
        return ras

    def create_or_model(self) -> tuple[list[ScheduleDay], list[Ra]]:
        '''
        Creates the OR model, adding constraints, and solving the problem
        '''
        # define variables
        staff_size = len(self.ra_availabilities)
        all_ras = self.create_ras()
        all_days = self.day_dict.values()
        total_days = len(all_days)

        model = cp_model.CpModel()
        self.revise_total_pts()

        # creating boolean variables (the assignments)
        assignments = {}
        for availability in all_ras:
            for day in all_days:
                for shift in range(day.ppl):
                    assignments[(availability, day, shift)] = model.new_bool_var(
                        (f'assignment_ra{availability}_date{day}_shift{shift}'))

        # adding hard constraints
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

        # ensure that an RA isn't scheduled to be on duty before they move in
        for availability, ra in zip(self.ra_availabilities, all_ras):
            for day in all_days:
                if (day.date <= availability.move_in_date):
                    for shift in range(day.ppl):
                        model.add(assignments[(ra, day, shift)] == 0)
                else:
                    break

        # dates that cannot be done
        for availability, ra in zip(self.ra_availabilities, all_ras):
            for date in availability.no_dates:
                if date in self.day_dict:
                    day = self.day_dict[date]
                    for shift in range(day.ppl):
                        model.add(assignments[(ra, day, shift)] == 0)

        no_days_dict = self.no_days_for_all_ras(all_ras)
        # days of the week that cannot be done
        for day in all_days:
            day_of_week = day.day_of_week
            for ra in no_days_dict[day_of_week]:
                for shift in range(day.ppl):
                    model.add(assignments[(ra, day, shift)] == 0)

        # new RAs cannot be on duty for the first 3 weeks (to account for shadow shifts)
        # new RAs to the community (but returners) cannot be on duty for the first 1.5 weeks
        for day_idx, day in zip(range(21), all_days):
            for ra in all_ras:
                if not ra.returner or (not ra.community_returner and day_idx <= 11):
                    for shift in range(day.ppl):
                        model.add(assignments[(ra, day, shift)] == 0)

        # only people on half staff can be on duty during break
        for date in self.holidays.breaks:
            day = self.day_dict[date]
            for ra in all_ras:
                if not ra.half_staff:
                    for shift in range(day.ppl):
                        model.add(assignments[(ra, day, shift)] == 0)

        # distribution, frontloading and backloading
        distribution_reward_new = 2
        distribution_reward_return = 4
        distribution_reward_double_return = 6
        reward_terms = []
        for availability, ra in zip(self.ra_availabilities, all_ras):
            distribution = availability.distribution
            distribution_reward = distribution_reward_new

            if (availability.community_returner):
                distribution_reward = distribution_reward_double_return
            elif (availability.returner):
                distribution_reward = distribution_reward_return

            for day_idx, day in zip(range(total_days), all_days):
                if (((day_idx < total_days / 2) and (distribution == Distribution.FRONTLOAD)) or
                        ((day_idx >= total_days / 2) and (distribution == Distribution.BACKLOAD))):
                    for shift in range(day.ppl):
                        reward_terms.append(
                            assignments[ra, day, shift] * distribution_reward)
                else:
                    for shift in range(day.ppl):
                        reward_terms.append(assignments[ra, day, shift])
        model.Maximize(sum(reward_terms))

        solver = cp_model.CpSolver()
        status = solver.solve(model)
        print(status)
    # Print solution.
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print('Solution found')
        # Print solution details and create schedule 
            schedule = []
            for day in all_days:
                day_schedule = ScheduleDay(day)
                print(f'Date: {day.date}, Day: {day.day_of_week}, Pts: {day.pts}')
                for ra in all_ras:
                    for shift in range(day.ppl):
                        if solver.Value(assignments[ra, day, shift]):
                            ra.pts += day.pts
                            day_schedule.add_ra(ra)
                            print(f'  RA {ra.name} works shift {shift}')
                schedule.append(day_schedule)

            for ra in all_ras:
                print(f'RA {ra.name} has {ra.pts} pts')
            print(solver.objective_value)
        else:
            print('No solution found')
        
        return schedule, all_ras