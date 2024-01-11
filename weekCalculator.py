import datetime

class WeekCalculator:
    def __init__(self, db, session, dailyDracking):
        self.db = db
        self.session =  session
        self.dayCalc = dailyDracking
        
    def getCurrentWeekDates(self): 
        today = datetime.date.today()
        currentWeekday = today.weekday() + 1
        startOfWeek = today - datetime.timedelta(days=currentWeekday)
        endOfWeek = startOfWeek + datetime.timedelta(days=6) 
        
        weekDates = []
        for i in range(7):
            date = startOfWeek + datetime.timedelta(days=i)
            weekDates.append(date)
        
        return weekDates

    def getCurrentWeekDatesStrings(self):
        weekDates = self.getCurrentWeekDates()
        weekDatesStrings = []
        for date in weekDates:
            weekDatesStrings.append(date.strftime("%Y-%m-%d"))
        return weekDatesStrings

    def getWeekTrackings(self):
        weekDatesStrings = self.getCurrentWeekDatesStrings()
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info, timestamp FROM timelog WHERE user_id ={user} and strftime('%Y-%m-%d', timestamp) in ('" + "','".join(weekDatesStrings)+"');")
        print(rows)
        return rows 

    def getDayHoursForDate(self, date)-> datetime.timedelta:
        rows = self.dayCalc.getTheDayTrackings(date)
        total = self.dayCalc.calcHours(rows)
        print(f"total {total}")
        return total

    def getWeekHours(self) -> tuple:
        weekDatesStrings = self.getCurrentWeekDatesStrings()
        dateHourList = []
        totalWeeekHours = datetime.timedelta()
        for date in weekDatesStrings:
            totalWeeekHours += self.getDayHoursForDate(date)
            dateHourList.append({'hours': self.getDayHoursForDate(date), 'date': date})
        return (totalWeeekHours, dateHourList)       


