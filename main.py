from duty_scheduler import DutyScheduler
from ra_availabilities import RaAvailability, DaysOfWeek, Distribution
from datetime import date

if __name__ == '__main__':
  ras = [RaAvailability("Kari", [date(2024, 1, 13), date(2024, 1, 14)], [DaysOfWeek.WEDNESDAY]),
         RaAvailability("Radhika", [date(2024, 1, 3), date(2024, 1, 4)], [DaysOfWeek.MONDAY, DaysOfWeek.FRIDAY]),
         RaAvailability("Annie"),
         RaAvailability("Elise"),
         RaAvailability("Luke"),
         RaAvailability("Megan", [date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6), date(2024, 3, 7), date(2024, 3, 8), date(2024, 3, 9), date(2024, 3, 10)], [DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY]),
         RaAvailability("Casey", [date(2024, 1, 8), date(2024, 1, 17), date(2024, 2, 25), date(2024, 3, 20), date(2024, 3, 1), date(2024, 3, 2), date(2024, 3, 3), date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6), date(2024, 3, 7), date(2024, 3, 8), date(2024, 3, 9), date(2024, 3, 10), date(2024, 4, 1), date(2024, 4, 5)],
                        [DaysOfWeek.WEDNESDAY, DaysOfWeek.THURSDAY]),
         RaAvailability("Matt", [date(2024, 1, 6), date(2024, 1, 7), date(2024, 2, 14), date(2024, 3, 26), date(2024, 3, 27)], [DaysOfWeek.TUESDAY]),
         RaAvailability("Grace", [date(2024, 1, 6), date(2024, 1, 7), date(2024, 2, 14), date(2024, 3, 27)]),
         RaAvailability("Tony", [date(2024, 3, 10), date(2024, 3, 11), date(2024, 3, 12), date(2024, 3, 13), date(2024, 3, 14), date(2024, 3, 15), date(2024, 3, 16), date(2024, 3, 17), date(2024, 3, 18)], [DaysOfWeek.SATURDAY]),
         RaAvailability("Nico"),
         RaAvailability("Tula", [date(2024, 2, 17), date(2024, 2, 18), date(2024, 2, 19), date(2024, 2, 20), date(2024, 2, 21), date(2024, 2, 22), date(2024, 2, 23), date(2024, 2, 24), date(2024, 2, 25)]),
         RaAvailability("Fortune", no_days=[DaysOfWeek.MONDAY, DaysOfWeek.TUESDAY, DaysOfWeek.WEDNESDAY]),
         RaAvailability("Selma", [date(2024, 2, 17), date(2024, 2, 18), date(2024, 2, 19), date(2024, 2, 20)], [DaysOfWeek.MONDAY]),
         RaAvailability("Tom", no_days=[DaysOfWeek.TUESDAY, DaysOfWeek.THURSDAY, DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY, DaysOfWeek.SUNDAY]),
         RaAvailability("Kaylee"),
         RaAvailability("Bella", [date(2024, 2, 15), date(2024, 2, 16), date(2024, 2, 17), date(2024, 2, 18), date(2024, 2, 19), date(2024, 3, 29), date(2024, 3, 1), date(2024, 3, 2), date(2024, 3, 3), date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6), date(2024, 3, 7), date(2024, 3, 8), date(2024, 3, 9), date(2024, 3, 10),]),
         RaAvailability("Julia", [date(2024, 1, 12), date(2024, 3, 30), date(2024, 3, 31)], [DaysOfWeek.THURSDAY]),
         RaAvailability("Ethan", [date(2024, 4, 14)], [DaysOfWeek.FRIDAY, DaysOfWeek.SATURDAY]),
         RaAvailability("Garett", [date(2024, 3, 12)], [DaysOfWeek.MONDAY, DaysOfWeek.TUESDAY, DaysOfWeek.WEDNESDAY]),
         RaAvailability("David"),
         RaAvailability("Karena"),
         RaAvailability("Derquan", [date(2024, 3, 29), date(2024, 3, 30), date(2024, 3, 31)], [DaysOfWeek.WEDNESDAY, DaysOfWeek.SATURDAY]),
         RaAvailability("Elizabeth", [date(2024, 1, 13), date(2024, 1, 14), date(2024, 1, 15), date(2024, 3, 17), date(2024, 3, 29), date(2024, 3, 30), date(2024, 3, 31)], [DaysOfWeek.THURSDAY]),
         RaAvailability("McKayla")]
  test = DutyScheduler('2024-01-02', '2024-05-06', 1, 2, ras)
  test.create_or_model()
  #print(test.all_dates_of_all_days())
  # weekdays = test.total_weekdays()
  # weekends = test.total_weekends()
  # shifts = test.weekend_shifts()
  # print(test.weekday_shifts())
  # print(weekends)
  # print(shifts)