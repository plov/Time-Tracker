from datetime import datetime

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
        result = {"startDay":True, 
                  "startLunch":True,
                  "finishLunch":True,
                  "finishDay":True}
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
    
    def calcHours(self, actions):
        if len(actions) == 0:
            return "00:00"
        actionsDict = {}
        actionList = self.getTimeActionsDict(actions)
        for item in actionList:
            actionsDict[item["info"]] = item["time"]
        dayHours = datetime.strptime(actionsDict["finishDay"], "%H:%M") - datetime.strptime(actionsDict["startDay"], "%H:%M")
        lunchHours = datetime.strptime(actionsDict["finishLunch"], "%H:%M") - datetime.strptime(actionsDict["startLunch"], "%H:%M")
        return dayHours - lunchHours

    def getTimeFromString(self, timestamp):
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        date_obj = datetime.strptime(timestamp, date_format)
        return date_obj.time().isoformat('minutes')
    
    
    