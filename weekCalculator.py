from datetime import timedelta, datetime, date
from collections import defaultdict

class WeekCalculator:
    def __init__(self, db, session, dailyDracking):
        self.db = db
        self.session =  session
        self.dayCalc = dailyDracking
        
    def getCurrentWeekDates(self): 
        today = date.today()
        currentWeekday = today.weekday() + 1
        startOfWeek = today - timedelta(days=currentWeekday)
        endOfWeek = startOfWeek + timedelta(days=6) 
        
        weekDates = []
        for i in range(7):
            dayDate = startOfWeek + timedelta(days=i)
            weekDates.append(dayDate)
        
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
        return rows 

    def getDayHoursForDate(self, data)-> timedelta:
        total = self.dayCalc.calcHoursPerDay(data)
        return total

    def getWeekHours(self) -> tuple:
        weekDatesStrings = self.getCurrentWeekDatesStrings()
        dateHourList = []
        totalWeeekHours = timedelta()
        rows = self.getWeekTrackings()
        datesDict = defaultdict(list)
        workedDatesDict = defaultdict(list)
        for date in weekDatesStrings:
            datesDict[date].append(('no work', date+' 00:00:00.0'))
        for row in rows:
            dayDate = row[1].split(" ")[0]
            workedDatesDict[dayDate].append(row)
        datesDict.update(workedDatesDict)
        datesLists = list(datesDict.values())
        for day in datesLists:
            if day[0][0] != 'no work':
                totalWeeekHours += self.getDayHoursForDate(day)
            dateHourList.append({'hours': self.getDayHoursForDate(day), 'date': day[0][1].split(" ")[0]})
        return (totalWeeekHours, dateHourList)     


