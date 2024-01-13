from datetime import timedelta, datetime
from constants import constants

class DailyTracking:

    def __init__(self, db, session):
        self.db = db
        self.session =  session

    def saveTimeLog(self, type, info, date = None):
        if date is None:
            timestamp = datetime.now()
        else:
            timestamp = date
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info FROM timelog WHERE user_id ={user} and strftime('%Y-%m-%d', timestamp) == strftime('%Y-%m-%d', date('now','localtime')) and info = '{info}';")
        if len(rows) == 0:
            self.db.executePush("INSERT INTO timelog (user_id,  timestamp, type, info) VALUES(?,?,?,?);", [user, timestamp, type, info])

    def checkIfDayStarted(self):
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info FROM timelog WHERE user_id ={user} and strftime('%Y-%m-%d', timestamp) == strftime('%Y-%m-%d', date('now','localtime')) and info = '{constants.START_DAY}';")
        if len(rows) == 0:
            return False
        else:
            return True
        
    def finishDayBefore(self):    
        rows = self.checkIfLastStartedDay()
        isLastDayFinished = self.checkIfLastDayFinished()
        print(f"isLastDayFinished: {isLastDayFinished}")
        if not isLastDayFinished:
            dateStr = rows[0][0]
            dateObj = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S.%f")
            dateObj = dateObj.replace(hour=23, minute=59, second=0, microsecond=0)
            date = dateObj.strftime("%Y-%m-%d %H:%M:%S.%f")
            print(f"date: {date}")
            self.saveTimeLog(constants.STOP_TYPE, constants.FINISH_DAY, date)
        return True
        
    def checkIfLastDayFinished(self):
        user = self.session["user_id"]
        rows = self.db.execute(f"""
            SELECT info
            FROM timelog 
            WHERE user_id = {user} 
            AND strftime('%Y-%m-%d', timestamp) = (
                SELECT MAX(strftime('%Y-%m-%d', timestamp)) 
                FROM timelog 
                WHERE user_id = {user}
            )
            AND info = '{constants.FINISH_DAY}';
        """)
        return len(rows) > 0
    
    def checkIfLastStartedDay(self):
        user = self.session["user_id"]
        rows = self.db.execute(f"""
            SELECT timestamp
            FROM timelog 
            WHERE user_id = {user} 
            AND strftime('%Y-%m-%d', timestamp) = (
                SELECT MAX(strftime('%Y-%m-%d', timestamp)) 
                FROM timelog 
                WHERE user_id = {user}
            )
            AND info = '{constants.START_DAY}';
        """)
        return rows

    def getTodayTrackings(self):
        #day = datetime.today().date() 
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info, timestamp FROM timelog WHERE user_id ={user} and strftime('%Y-%m-%d', timestamp) == strftime('%Y-%m-%d', date('now','localtime'));")
        return rows
        
    def getTheDayTrackings(self, selectedDate):
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info, timestamp FROM timelog WHERE user_id ={user} and strftime('%Y-%m-%d', timestamp) = '"+selectedDate+"';")
        return rows
    
    def awailableActions2List(self, actions):
        result = []
        for action in actions:
            for item in action:
                result.append(item) 
        return list(set(result))
    
    def checkAvailableActions(self, actions) -> dict:
        result = {constants.START_DAY:True, 
                  constants.START_LUNCH:True,
                  constants.FINISH_LUNCH:True,
                  constants.FINISH_DAY:True}
        actionList = self.awailableActions2List(actions)
        for item in actionList:
            result[item] = False
        return result
    
    def getTimeActionsDict(self, actions) -> dict:
        result = []
        for action in actions:
            time = self.getTimeFromString(action[1])
            result.append({"info":action[0], "time":time})
        return result
    
    def calcHoursPerDay(self, actions)-> timedelta:
        if len(actions) == 0:
            return timedelta()
        actionsDict = {}
        actionList = self.getTimeActionsDict(actions)
        for item in actionList:
            actionsDict[item["info"]] = item["time"]
        
        dayHours = timedelta()
        lunchHours = timedelta()
        if constants.FINISH_DAY in actionsDict and constants.START_DAY in actionsDict:   
            dayHours = datetime.strptime(actionsDict[constants.FINISH_DAY], "%H:%M") - datetime.strptime(actionsDict[constants.START_DAY], "%H:%M")
        if constants.FINISH_LUNCH in actionsDict and constants.START_LUNCH in actionsDict:
            lunchHours = datetime.strptime(actionsDict[constants.FINISH_LUNCH], "%H:%M") - datetime.strptime(actionsDict[constants.START_LUNCH], "%H:%M")
            return dayHours - lunchHours
        else:
            return dayHours

    def getTimeFromString(self, timestamp):
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        date_obj = datetime.strptime(timestamp, date_format)
        return date_obj.time().isoformat('minutes')
    
    
    