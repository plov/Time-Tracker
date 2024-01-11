from datetime import timedelta, datetime
from constants import constants

class DailyTracking:

    def __init__(self, db, session):
        self.db = db
        self.session =  session

    def saveTimeLog(self, type, info):
        timestamp = datetime.now()
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info FROM timelog WHERE user_id ={user} and strftime('%d', timestamp) == strftime('%d', date('now','localtime')) and info = '{info}';")
        if len(rows) == 0:
            self.db.executePush("INSERT INTO timelog (user_id,  timestamp, type, info) VALUES(?,?,?,?);", [user, timestamp, type, info])

    def getTodayTrackings(self):
        #day = datetime.today().date() 
        user = self.session["user_id"]
        rows = self.db.execute(f"SELECT info, timestamp FROM timelog WHERE user_id ={user} and strftime('%d', timestamp) == strftime('%d', date('now','localtime'));")
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
                  constants.FINIFH_LUNCH:True,
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
    
    def calcHours(self, actions)-> timedelta:
        if len(actions) == 0:
            return timedelta()
        actionsDict = {}
        actionList = self.getTimeActionsDict(actions)
        for item in actionList:
            actionsDict[item["info"]] = item["time"]
        if constants.FINISH_DAY in actionsDict and constants.START_DAY in actionsDict:   
            dayHours = datetime.strptime(actionsDict[constants.FINISH_DAY], "%H:%M") - datetime.strptime(actionsDict[constants.START_DAY], "%H:%M")
            lunchHours = datetime.strptime(actionsDict[constants.FINIFH_LUNCH], "%H:%M") - datetime.strptime(actionsDict[constants.START_LUNCH], "%H:%M")
            return dayHours - lunchHours
        else:
            return timedelta()

    def getTimeFromString(self, timestamp):
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        date_obj = datetime.strptime(timestamp, date_format)
        return date_obj.time().isoformat('minutes')
    
    
    