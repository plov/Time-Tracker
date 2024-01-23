from datetime import timedelta, datetime, date
from collections import defaultdict

class WeekCalculator:
    def __init__(self, db, session, daily_trackings):
        self.db = db
        self.session =  session
        self.day_calc = daily_trackings
        
    def get_dates_of_current_week(self): 
        today = date.today()
        current_weekday = today.weekday() + 1
        start_of_week = today - timedelta(days=current_weekday)
        
        week_dates = []
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            week_dates.append(day_date)
        
        return week_dates

    def current_week_dates_2_strings(self):
        week_dates = self.get_dates_of_current_week()
        week_dates_strings = []
        for date in week_dates:
            week_dates_strings.append(date.strftime("%Y-%m-%d"))
        return week_dates_strings

    def week_trackings(self):
        user = self.session["user_id"]
        rows = self.db.execute("""
                               SELECT info, timestamp 
                               FROM timelog 
                               WHERE user_id =?
                               and strftime('%Y-%m-%d', timestamp) in ('" + "','".join(week_dates_strings)+"');
                               """, [user])
        return rows 

    def week_hours(self) -> tuple:
        week_dates_strings = self.current_week_dates_2_strings()
        date_hours_list = []
        total_weeek_hours = timedelta()
        rows = self.week_trackings()
        dates_dict = defaultdict(list)
        worked_dates_dict = defaultdict(list)
        for date in week_dates_strings:
            dates_dict[date].append(('no work', date+' 00:00:00.0'))
        for row in rows:
            day_date = row[1].split(" ")[0]
            worked_dates_dict[day_date].append(row)
        dates_dict.update(worked_dates_dict)
        datesLists = list(dates_dict.values())
        for day in datesLists:
            if day[0][0] != 'no work':
                total_weeek_hours += self.day_calc.calc_day_hours(day)
            date_hours_list.append({'hours': self.day_calc.calc_day_hours(day), 'date': day[0][1].split(" ")[0]})
        return (total_weeek_hours, date_hours_list)     


